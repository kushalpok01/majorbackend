import logging

from app.engines.nepali_voice_engine import NepaliVoiceEngine

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self) -> None:
        self._engine = NepaliVoiceEngine()
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        logger.info("Initializing TTS service with Nepali voice conversion engine")
        try:
            self._engine.load_model()
        except Exception:
            logger.exception("Voice model failed during startup; service remains available")

        self._initialized = True

    def synthesize(self, text: str, target_wav_path: str) -> str:
        if not self._initialized:
            raise RuntimeError("TTS service not initialized")

        try:
            return self._engine.synthesize(text=text, target_wav_path=target_wav_path)
        except Exception as exc:
            logger.exception("Voice synthesis failed")
            raise RuntimeError(f"Voice synthesis failed: {exc}") from exc


tts_service = TTSService()


def initialize_tts_service() -> None:
    tts_service.initialize()


def generate_speech(text: str, target_wav_path: str) -> str:
    return tts_service.synthesize(text=text, target_wav_path=target_wav_path)
