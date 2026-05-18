import numpy as np


def texture_analysis(frame: np.ndarray) -> dict:
    gray = frame.mean(axis=2).astype(np.float32)
    gx = np.abs(np.diff(gray, axis=1)).mean() if gray.shape[1] > 1 else 0.0
    gy = np.abs(np.diff(gray, axis=0)).mean() if gray.shape[0] > 1 else 0.0
    variance = gray.var()
    texture = float((gx + gy) / max(1.0, variance**0.5))
    return {
        "module": "texture",
        "score": float(min(1.0, texture / 3.0)),
        "details": {"gradient_x": float(gx), "gradient_y": float(gy), "variance": float(variance)},
    }
