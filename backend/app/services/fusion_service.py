from collections import defaultdict
from typing import Dict


class FusionService:
    """Weighted fusion of face and speech emotion distributions."""

    def __init__(self, face_weight: float = 0.6, speech_weight: float = 0.4) -> None:
        weight_total = face_weight + speech_weight
        if weight_total <= 0:
            raise ValueError("Fusion weights must sum to a positive value")

        self.face_weight = face_weight / weight_total
        self.speech_weight = speech_weight / weight_total

    def fuse(self, face_scores: Dict[str, float], speech_scores: Dict[str, float]) -> Dict[str, object]:
        fused = defaultdict(float)

        for emotion, score in face_scores.items():
            fused[emotion] += self.face_weight * score
        for emotion, score in speech_scores.items():
            fused[emotion] += self.speech_weight * score

        total = sum(fused.values()) or 1.0
        fused_scores = {emotion: value / total for emotion, value in fused.items()}

        top_emotion = max(fused_scores, key=fused_scores.get)
        return {
            "emotion": top_emotion,
            "confidence": float(fused_scores[top_emotion]),
            "fused_scores": fused_scores,
        }
