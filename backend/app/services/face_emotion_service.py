import logging
from typing import Dict

import numpy as np

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
            return {
                "top_emotion": "neutral",
                "confidence": 0.0,
                "scores": {"neutral": 1.0},
                "provider": f"{self.provider_name}-unavailable",
            }

        result = self._deepface.analyze(img_path=image, actions=["emotion"], enforce_detection=False)
        if isinstance(result, list):
            result = result[0]

        emotions = {k: float(v) / 100.0 for k, v in result["emotion"].items()}
        top_emotion = max(emotions, key=emotions.get)

        return {
            "top_emotion": top_emotion,
            "confidence": float(emotions[top_emotion]),
            "scores": emotions,
            "provider": self.provider_name,
        }
