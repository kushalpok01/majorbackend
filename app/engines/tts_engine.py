import io
import logging
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from uuid import uuid4

from gtts import gTTS

from app.engines.base import TTSEngine

logger = logging.getLogger(__name__)

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


@dataclass(frozen=True)
class SynthesizedAudio:
    data: bytes
    media_type: str
    filename: str


class HybridTTSEngine(TTSEngine):
    def __init__(self) -> None:
        self._lock = Lock()
        self._local_engine = None
        self._local_ready = False
        self._tmp_dir = Path(tempfile.gettempdir()) / "fastapi_tts"
        self._tmp_dir.mkdir(parents=True, exist_ok=True)
        self._local_init_error: str | None = None

    @property
    def name(self) -> str:
        return "hybrid"

    def load_model(self) -> None:
        if self._local_ready:
            return

        try:
            import pyttsx3

            engine = pyttsx3.init(driverName="sapi5")
            engine.setProperty("rate", 170)
            engine.setProperty("volume", 1.0)

            voices = engine.getProperty("voices") or []
            selected_voice_id = None
            for voice in voices:
                langs = getattr(voice, "languages", None) or []
                lang_blob = " ".join(str(item).lower() for item in langs)
                name_blob = str(getattr(voice, "name", "")).lower()
                if "en" in lang_blob or "english" in name_blob:
                    selected_voice_id = voice.id
                    break
            if selected_voice_id:
                engine.setProperty("voice", selected_voice_id)

            self._local_engine = engine
            self._local_ready = True
            self._local_init_error = None
            logger.info("Local English TTS initialized")
        except Exception as exc:
            self._local_engine = None
            self._local_ready = False
            self._local_init_error = str(exc)
            logger.exception("Local English TTS initialization failed")

    def synthesize(self, text: str) -> bytes:
        return self.synthesize_audio(text=text, lang="").data

    def synthesize_audio(self, text: str, lang: str = "") -> SynthesizedAudio:
        clean_text = (text or "").strip()
        if not clean_text:
            raise RuntimeError("Input text cannot be empty")

        if not self._local_ready and self._local_engine is None:
            self.load_model()

        language = self._normalize_lang(lang) or self._detect_language(clean_text)
        if language == "ne":
            return self._synthesize_nepali(clean_text)
        return self._synthesize_english(clean_text)

    def _synthesize_nepali(self, text: str) -> SynthesizedAudio:
        try:
            return self._synthesize_gtts(text=text, lang="ne")
        except Exception:
            logger.exception("Nepali synthesis via gTTS(ne) failed, trying gTTS(en)")
            try:
                return self._synthesize_gtts(text=text, lang="en")
            except Exception as exc:
                logger.exception("Nepali fallback synthesis failed")
                raise RuntimeError("Nepali TTS synthesis failed") from exc

    def _synthesize_english(self, text: str) -> SynthesizedAudio:
        if self._local_ready and self._local_engine is not None:
            try:
                return self._synthesize_local_wav(text)
            except Exception:
                logger.exception("Local English TTS failed, falling back to gTTS")

        try:
            return self._synthesize_gtts(text=text, lang="en")
        except Exception as exc:
            logger.exception("English gTTS fallback failed")
            raise RuntimeError("English TTS synthesis failed") from exc

    def _synthesize_gtts(self, text: str, lang: str) -> SynthesizedAudio:
        buffer = io.BytesIO()
        gTTS(text=text, lang=lang, slow=False).write_to_fp(buffer)
        data = buffer.getvalue()
        if not data:
            raise RuntimeError("gTTS returned empty audio")
        return SynthesizedAudio(
            data=data,
            media_type="audio/mpeg",
            filename="speech.mp3",
        )

    def _synthesize_local_wav(self, text: str) -> SynthesizedAudio:
        if not self._local_ready or self._local_engine is None:
            raise RuntimeError(
                f"Local TTS engine unavailable: {self._local_init_error or 'unknown'}"
            )

        out_path = self._tmp_dir / f"tts_{uuid4().hex}.wav"
        with self._lock:
            self._local_engine.save_to_file(text, str(out_path))
            self._local_engine.runAndWait()
            self._local_engine.stop()

        try:
            data = out_path.read_bytes()
            if not data:
                raise RuntimeError("Local TTS produced empty audio")
            return SynthesizedAudio(
                data=data,
                media_type="audio/wav",
                filename="speech.wav",
            )
        finally:
            try:
                out_path.unlink(missing_ok=True)
            except Exception:
                logger.warning("Temporary audio cleanup failed: %s", out_path)

    @staticmethod
    def _detect_language(text: str) -> str:
        return "ne" if _DEVANAGARI_RE.search(text) else "en"

    @staticmethod
    def _normalize_lang(lang: str) -> str:
        value = (lang or "").strip().lower()
        if value in {"ne", "nep", "nepali"}:
            return "ne"
        if value in {"en", "eng", "english"}:
            return "en"
        return ""
