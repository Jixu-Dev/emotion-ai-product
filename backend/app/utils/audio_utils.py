import base64
import io
from typing import Tuple

import librosa
import numpy as np
import soundfile as sf
from fastapi import HTTPException


def strip_data_uri_prefix(data: str) -> str:
    if "," in data and data.split(",", 1)[0].startswith("data:"):
        return data.split(",", 1)[1]
    return data


def decode_base64_audio(audio_base64: str, target_sr: int = 16_000) -> Tuple[np.ndarray, int]:
    """Decode base64 audio bytes and resample for model inference."""

    try:
        audio_bytes = base64.b64decode(strip_data_uri_prefix(audio_base64), validate=True)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid base64 audio payload") from exc

    buffer = io.BytesIO(audio_bytes)

    try:
        signal, sr = sf.read(buffer, always_2d=False)
        if signal.ndim > 1:
            signal = np.mean(signal, axis=1)
        signal = signal.astype(np.float32)
    except Exception:  # noqa: BLE001
        buffer.seek(0)
        try:
            signal, sr = librosa.load(buffer, sr=None, mono=True)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail="Unable to decode audio payload") from exc

    if signal.size == 0:
        raise HTTPException(status_code=400, detail="Audio payload is empty")

    if sr != target_sr:
        signal = librosa.resample(signal, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    return signal, sr
