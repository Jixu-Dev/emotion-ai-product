from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.schemas.emotion_schema import (
    FaceEmotionRequest,
    FaceEmotionResponse,
    FusionRequest,
    FusionResponse,
    SpeechEmotionRequest,
    SpeechEmotionResponse,
)
from app.services.face_emotion_service import FaceEmotionService
from app.services.fusion_service import FusionService
from app.services.insight_service import InsightService
from app.services.speech_emotion_service import SpeechEmotionService
from app.utils.audio_utils import decode_base64_audio
from app.utils.image_utils import decode_base64_image

router = APIRouter(prefix="/emotion", tags=["emotion"])

settings = get_settings()
face_service = FaceEmotionService()
speech_service = SpeechEmotionService(device=settings.torch_device)
fusion_service = FusionService(face_weight=settings.face_weight, speech_weight=settings.speech_weight)
insight_service = InsightService()


@router.post("/face", response_model=FaceEmotionResponse)
def analyze_face_emotion(payload: FaceEmotionRequest) -> FaceEmotionResponse:
    try:
        image = decode_base64_image(payload.image_base64)
        prediction = face_service.analyze(image)
        return FaceEmotionResponse(**prediction)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to process face emotion request") from exc


@router.post("/speech", response_model=SpeechEmotionResponse)
def analyze_speech_emotion(payload: SpeechEmotionRequest) -> SpeechEmotionResponse:
    target_sr = payload.sample_rate or 16_000
    signal, sample_rate = decode_base64_audio(payload.audio_base64, target_sr=target_sr)
    prediction = speech_service.analyze(signal, sample_rate)
    return SpeechEmotionResponse(speech=prediction)


@router.post("/fusion", response_model=FusionResponse)
def analyze_multimodal_emotion(payload: FusionRequest) -> FusionResponse:
    fused = fusion_service.fuse(face_scores=payload.face.scores, speech_scores=payload.speech.scores)
    insight = insight_service.generate(fused["emotion"], fused["confidence"])
    return FusionResponse(**fused, insight=insight)
