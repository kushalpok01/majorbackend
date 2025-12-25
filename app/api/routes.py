# app/api/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import MessageRequest
from app.services.tts_service import generate_speech

router = APIRouter()

@router.post("/message")
def text_to_speech(body: MessageRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    audio_path = generate_speech(text)

    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename="speech.wav"
    )
