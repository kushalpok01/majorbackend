import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.models.schemas import MessageRequest
from app.services.tts_service import generate_speech

router = APIRouter()
logger = logging.getLogger(__name__)
DEFAULT_TARGET_WAV = Path("app/assets/default_speaker.wav").resolve()


def _cleanup_file(path: str) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        logger.exception("Failed to clean temporary output file: %s", path)


@router.post("/message")
def text_to_speech(body: MessageRequest, background_tasks: BackgroundTasks):
    text = (body.text or "").strip()
    target_wav_path = (body.target_wav_path or "").strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    selected_target_path = target_wav_path or str(DEFAULT_TARGET_WAV)

    try:
        converted_path = generate_speech(text=text, target_wav_path=selected_target_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("TTS generation failed")
        raise HTTPException(status_code=500, detail="TTS generation failed")

    background_tasks.add_task(_cleanup_file, converted_path)
    return FileResponse(
        path=converted_path,
        media_type="audio/wav",
        filename="converted.wav",
    )
