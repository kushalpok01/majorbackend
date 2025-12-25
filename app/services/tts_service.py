from pathlib import Path

AUDIO_PATH = Path("app/static/audio/mock.mp3")

def generate_speech(text: str) -> Path:
    """
    Mock TTS function.
    Later this will call the ML model.
    """
    return AUDIO_PATH
