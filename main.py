from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="TTS Backend",
            description="Generates speech from Nepali Devanagari text using ML models",
            version="1.0.0",)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8080"],
    # allow_origins=["https://id-preview--9dfbfdc3-c5a2-4b61-955b-35cc6e5096d9.lovable.app/*"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
