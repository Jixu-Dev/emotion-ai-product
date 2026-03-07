from typing import Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    version: str


class FaceEmotionRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image or data URI")


class SpeechEmotionRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded WAV/MP3 audio or data URI")
    sample_rate: Optional[int] = Field(None, description="Optional desired sample rate")


class EmotionPrediction(BaseModel):
    top_emotion: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    scores: Dict[str, float]


class FaceEmotionResponse(EmotionPrediction):
    pass


class SpeechEmotionResponse(BaseModel):
    speech: EmotionPrediction


class FusionRequest(BaseModel):
    face: EmotionPrediction
    speech: EmotionPrediction


class FusionResponse(BaseModel):
    emotion: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    fused_scores: Dict[str, float]
    insight: str
