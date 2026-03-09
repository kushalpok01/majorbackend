from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.services.tts_service import initialize_tts_service

app = FastAPI(
    title="TTS Backend",
    description="Generates speech from Nepali Devanagari text using ML models",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    initialize_tts_service()


app.include_router(router)


@app.get("/")
def root():
    return {"status": "Backend running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
