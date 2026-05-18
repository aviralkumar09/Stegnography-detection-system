import numpy as np


def histogram_analysis(frame: np.ndarray) -> dict:
    gray = frame.mean(axis=2).astype(np.uint8)
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    smoothness = np.mean(np.abs(np.diff(hist)))
    norm = smoothness / max(1.0, hist.max())
    return {
        "module": "histogram",
        "score": float(min(1.0, norm / 5.0)),
        "details": {"smoothness": float(smoothness)},
    }
