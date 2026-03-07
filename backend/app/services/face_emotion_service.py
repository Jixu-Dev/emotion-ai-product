import logging
from typing import Dict

import numpy as np
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class FaceEmotionService:
    """Face emotion detector powered by DeepFace."""

    provider_name = "deepface"

    def __init__(self) -> None:
        try:
            from deepface import DeepFace  # noqa: PLC0415

            self._deepface = DeepFace
            self._is_available = True
        except Exception as exc:  # noqa: BLE001
            logger.warning("DeepFace could not be imported: %s", exc)
            self._deepface = None
            self._is_available = False

    def analyze(self, image: np.ndarray) -> Dict[str, object]:
        if not self._is_available or self._deepface is None:
            raise HTTPException(status_code=503, detail="Face emotion service is unavailable")

        try:
            # DeepFace can return either a dict or a list[dict] depending on the version.
            result = self._deepface.analyze(image, actions=["emotion"], enforce_detection=False)
        except Exception as exc:  # noqa: BLE001
            logger.exception("DeepFace analysis failed")
            raise HTTPException(status_code=500, detail="Failed to analyze face emotion") from exc

        if isinstance(result, dict):
            result = [result]

        if not isinstance(result, list) or not result or not isinstance(result[0], dict):
            raise HTTPException(status_code=422, detail="Invalid response returned by DeepFace")

        emotion_scores = result[0]["emotion"]
        top_emotion = result[0]["dominant_emotion"]

        scores = {str(label): float(value) for label, value in emotion_scores.items()}

        confidence = scores[top_emotion] / 100

        return {
            "top_emotion": top_emotion,
            "confidence": confidence,
            "scores": scores,
        }
