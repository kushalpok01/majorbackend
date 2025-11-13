# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

# === FastAPI app ===
app = FastAPI(title="AI Script Generator Backend")

# === Allow your React app to connect ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:5173"] or your domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Models ===
class MessageRequest(BaseModel):
    text: str

class GeneratedClip(BaseModel):
    id: str
    name: str
    duration: float
    status: str


# === Temporary storage ===
generated_clips = []


# === Routes ===

@app.get("/")
def read_root():
    return {"message": "Backend is live!"}


@app.post("/message")
def handle_message(body: MessageRequest):
    """
    Endpoint that handles message from frontend.
    Matches: PostRequest("message", body)
    """
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message text cannot be empty.")

    # Simulate text processing (e.g. AI reply or speech generation)
    response_text = f"Processed text: {text}"

    # Simulate generating a new audio clip
    new_clip = GeneratedClip(
        id=str(uuid.uuid4()),
        name=f"Clip {len(generated_clips) + 1}",
        duration=len(text) * 0.12,  # fake duration
        status="ready"
    )
    generated_clips.append(new_clip)

    # Return simulated AI result (can be text + clip)
    return {
        "message": response_text,
        # "clip": new_clip
    }
@app.post("/prompt")
def handle_message(body: MessageRequest):
    """
    Endpoint that handles prompt for AI script generation request from frontend.
    Matches: PostRequest("prompt", body)
    """
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Prompt text cannot be empty.")

    # Simulate text processing (e.g. AI reply or speech generation)
    response_text = f"Processed prompt: {text}"

    # Simulate generating a new audio clip
    new_clip = GeneratedClip(
        id=str(uuid.uuid4()),
        name=f"Clip {len(generated_clips) + 1}",
        duration=len(text) * 0.12,  # fake duration
        status="ready"
    )
    generated_clips.append(new_clip)

    # Return simulated AI result (can be text + clip)
    return {
        "message": response_text,
        # "clip": new_clip
    }


@app.get("/clips")
def get_clips():
    """Return all generated clips"""
    return generated_clips


@app.delete("/clips/{clip_id}")
def delete_clip(clip_id: str):
    """Delete a clip by ID"""
    global generated_clips
    before = len(generated_clips)
    generated_clips = [c for c in generated_clips if c.id != clip_id]
    if len(generated_clips) == before:
        raise HTTPException(status_code=404, detail="Clip not found.")
    return {"message": "Deleted successfully"}
