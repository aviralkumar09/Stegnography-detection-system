import numpy as np


def chi_square_analysis(frame: np.ndarray) -> dict:
    gray = frame.mean(axis=2).astype(np.uint8).flatten()
    lsb = gray & 1
    observed = np.bincount(lsb, minlength=2).astype(np.float64)
    expected = np.array([gray.size / 2, gray.size / 2], dtype=np.float64)
    chi = float(np.sum((observed - expected) ** 2 / np.maximum(expected, 1.0)))
    return {
        "module": "chi_square",
        "score": min(1.0, chi / 10.0),
        "details": {"chi_square": chi, "lsb_distribution": observed.tolist()},
    }
