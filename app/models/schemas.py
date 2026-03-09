from pydantic import BaseModel


class MessageRequest(BaseModel):
    text: str
    target_wav_path: str | None = None
    lang: str | None = None
