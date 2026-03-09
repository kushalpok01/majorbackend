import io
import logging
import math
import struct
from threading import Lock
from typing import Any

from app.engines.base import TTSEngine

logger = logging.getLogger(__name__)


class FastSpeechEngine(TTSEngine):
    """FastSpeech engine adapter with safe startup and synthesis fallback."""

    def __init__(self) -> None:
        self._tts: Any | None = None
        self._ready = False
        self._lock = Lock()

    @property
    def name(self) -> str:
        return "fastspeech"

    def load_model(self) -> None:
        if self._ready:
            return

        logger.info("Initializing FastSpeech engine")
        try:
            # Hook for real model initialization.
            # Example: self._tts = YourFastSpeechModel.load_from_checkpoint(...)
            self._tts = self._load_fastspeech_model()
            self._ready = True
            logger.info("FastSpeech engine initialized")
        except Exception:
            self._tts = None
            self._ready = False
            logger.exception("FastSpeech engine failed to initialize")

    def synthesize(self, text: str) -> bytes:
        if not self._ready:
            raise RuntimeError("FastSpeech model is not loaded")

        with self._lock:
            try:
                # Replace this with model inference when wiring FastSpeech output.
                # FastSpeech is single-speaker; no speaker-manager handling is used.
                duration_seconds = max(0.5, min(len(text) * 0.03, 3.0))
                return _generate_beep_wav(duration_seconds=duration_seconds)
            except Exception:
                logger.exception("FastSpeech inference failed")
                raise

    def _load_fastspeech_model(self) -> Any | None:
        """Load and return the FastSpeech model instance."""
        # Intentionally no-op until real FastSpeech weights/runtime are integrated.
        return object()


def _generate_beep_wav(duration_seconds: float, sample_rate: int = 22050, frequency_hz: float = 220.0) -> bytes:
    total_samples = int(duration_seconds * sample_rate)
    amplitude = 0.2

    pcm_data = bytearray()
    for i in range(total_samples):
        sample = amplitude * math.sin(2.0 * math.pi * frequency_hz * (i / sample_rate))
        pcm_data.extend(struct.pack("<h", int(sample * 32767)))

    byte_rate = sample_rate * 2
    block_align = 2
    data_size = len(pcm_data)
    riff_size = 36 + data_size

    header = io.BytesIO()
    header.write(b"RIFF")
    header.write(struct.pack("<I", riff_size))
    header.write(b"WAVE")
    header.write(b"fmt ")
    header.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, byte_rate, block_align, 16))
    header.write(b"data")
    header.write(struct.pack("<I", data_size))
    header.write(pcm_data)

    return header.getvalue()
