import numpy as np


def anomaly_detection(frame: np.ndarray) -> dict:
    gray = frame.mean(axis=2).astype(np.float32)
    feature_vector = np.array(
        [
            gray.mean() / 255.0,
            gray.std() / 255.0,
            np.percentile(gray, 90) / 255.0,
            np.percentile(gray, 10) / 255.0,
        ],
        dtype=np.float32,
    )
    baseline = np.array([0.5, 0.2, 0.8, 0.2], dtype=np.float32)
    distance = float(np.linalg.norm(feature_vector - baseline))
    return {
        "module": "anomaly",
        "score": float(min(1.0, distance * 1.6)),
        "details": {"distance": distance, "feature_vector": feature_vector.tolist()},
    }
