import logging
import subprocess
import tempfile
import warnings
from pathlib import Path
from threading import Lock
from uuid import uuid4

from gtts import gTTS

logger = logging.getLogger(__name__)


class NepaliVoiceEngine:
    def __init__(self) -> None:
        self._model_name = "voice_conversion_models/multilingual/vctk/freevc24"
        self._model = None
        self._is_loaded = False
        self._load_error: str | None = None
        self._model_lock = Lock()
        self._synthesis_lock = Lock()

    @property
    def name(self) -> str:
        return "nepali_voice"

    def load_model(self) -> None:
        if self._is_loaded and self._model is not None:
            return

        with self._model_lock:
            if self._is_loaded and self._model is not None:
                return

            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        message=r"You are using `torch\.load` with `weights_only=False`.*",
                        category=FutureWarning,
                    )
                    from TTS.api import TTS

                    self._model = TTS(model_name=self._model_name, progress_bar=False, gpu=False)

                self._is_loaded = True
                self._load_error = None
                logger.info("Loaded voice conversion model: %s", self._model_name)
            except Exception as exc:
                self._model = None
                self._is_loaded = False
                self._load_error = str(exc)
                logger.exception("Failed to load voice conversion model")

    def synthesize(self, text: str, target_wav_path: str) -> str:
        clean_text = (text or "").strip()
        if not clean_text:
            raise ValueError("Input text cannot be empty")

        target_path = Path(target_wav_path).expanduser().resolve()
        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundError(f"Target speaker wav not found: {target_path}")

        self.load_model()
        if not self._is_loaded or self._model is None:
            raise RuntimeError(
                f"Voice model unavailable: {self._load_error or 'unknown initialization error'}"
            )

        output_root = Path(tempfile.gettempdir()) / "fastapi_tts_outputs"
        output_root.mkdir(parents=True, exist_ok=True)
        output_path = output_root / f"converted_{uuid4().hex}.wav"

        try:
            with tempfile.TemporaryDirectory(prefix="nepali_vc_") as tmp_dir:
                temp_dir = Path(tmp_dir)
                source_mp3 = temp_dir / "source.mp3"
                source_wav = temp_dir / "source.wav"

                self._generate_source_wav(clean_text, source_mp3=source_mp3, source_wav=source_wav)

                with self._synthesis_lock:
                    self._model.voice_conversion_to_file(
                        source_wav=str(source_wav),
                        target_wav=str(target_path),
                        file_path=str(output_path),
                    )

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError("Voice conversion produced empty output")

            return str(output_path)

        except Exception as exc:
            logger.exception("Nepali voice synthesis failed")
            try:
                output_path.unlink(missing_ok=True)
            except Exception:
                logger.warning("Failed to clean partial output file: %s", output_path)
            raise RuntimeError("Nepali voice synthesis failed") from exc

    def _generate_source_wav(self, text: str, source_mp3: Path, source_wav: Path) -> None:
        try:
            gTTS(text=text, lang="ne", slow=False).save(str(source_mp3))
        except Exception as exc:
            logger.exception("gTTS generation failed")
            raise RuntimeError("gTTS generation failed") from exc

        if not source_mp3.exists() or source_mp3.stat().st_size == 0:
            raise RuntimeError("gTTS produced empty source audio")

        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(str(source_mp3), format="mp3")
            audio = audio.set_channels(1).set_frame_rate(24000)
            audio.export(str(source_wav), format="wav")
        except Exception:
            logger.exception("pydub conversion failed; trying ffmpeg fallback")
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(source_mp3),
                        "-ac",
                        "1",
                        "-ar",
                        "24000",
                        str(source_wav),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except Exception as exc:
                logger.exception("Failed to convert mp3 to wav")
                raise RuntimeError("Failed to convert gTTS output to wav") from exc

        if not source_wav.exists() or source_wav.stat().st_size == 0:
            raise RuntimeError("Source wav conversion failed")
