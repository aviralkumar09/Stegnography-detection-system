import numpy as np


def ai_detection(frame: np.ndarray) -> dict:
    flat = frame.astype(np.float32).reshape(-1, 3)
    mean_channels = flat.mean(axis=0) / 255.0
    std_channels = flat.std(axis=0) / 255.0
    logits = (0.8 * std_channels.mean()) + (0.2 * abs(mean_channels[0] - mean_channels[1]))
    probability = float(1 / (1 + np.exp(-8 * (logits - 0.2))))
    return {
        "module": "ai_detection",
        "score": probability,
        "details": {
            "model": "lightweight_cnn_proxy",
            "probability": probability,
            "mean_channels": mean_channels.tolist(),
            "std_channels": std_channels.tolist(),
        },
    }
