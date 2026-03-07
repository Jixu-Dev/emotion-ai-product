from typing import Dict, List

import librosa
import numpy as np
import torch
import torch.nn as nn


class _PlaceholderSpeechEmotionModel(nn.Module):
    """Small placeholder network for speech emotion scoring."""

    def __init__(self, in_features: int, out_features: int) -> None:
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)

        with torch.no_grad():
            nn.init.xavier_uniform_(self.linear.weight)
            nn.init.zeros_(self.linear.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


class SpeechEmotionService:
    provider_name = "librosa-torch-placeholder"
    labels: List[str] = ["neutral", "happy", "sad", "angry", "fear", "surprise"]

    def __init__(self, device: str = "cpu") -> None:
        self.device = torch.device(device)
        self.model = _PlaceholderSpeechEmotionModel(in_features=7, out_features=len(self.labels)).to(self.device)
        self.model.eval()

    def _extract_features(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        mfcc = librosa.feature.mfcc(y=signal, sr=sample_rate, n_mfcc=4)
        zcr = librosa.feature.zero_crossing_rate(y=signal)
        rms = librosa.feature.rms(y=signal)
        spectral_centroid = librosa.feature.spectral_centroid(y=signal, sr=sample_rate)

        features = np.array(
            [
                float(np.mean(mfcc[0])),
                float(np.mean(mfcc[1])),
                float(np.mean(mfcc[2])),
                float(np.mean(mfcc[3])),
                float(np.mean(zcr)),
                float(np.mean(rms)),
                float(np.mean(spectral_centroid)),
            ],
            dtype=np.float32,
        )

        return features

    def analyze(self, signal: np.ndarray, sample_rate: int) -> Dict[str, object]:
        features = self._extract_features(signal, sample_rate)
        tensor = torch.tensor(features, dtype=torch.float32, device=self.device).unsqueeze(0)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

        scores = {label: float(probs[idx]) for idx, label in enumerate(self.labels)}
        top_emotion = max(scores, key=scores.get)

        return {
            "top_emotion": top_emotion,
            "confidence": float(scores[top_emotion]),
            "scores": scores,
            "provider": self.provider_name,
        }
