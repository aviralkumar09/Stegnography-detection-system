import numpy as np


def rs_analysis(frame: np.ndarray) -> dict:
    blocks = frame.mean(axis=2).astype(np.int16).flatten()
    cutoff = (blocks.size // 4) * 4
    if cutoff == 0:
        return {
            "module": "rs_analysis",
            "score": 0.0,
            "details": {"regular": 0, "singular": 0, "imbalance": 0.0},
        }
    grouped = blocks[:cutoff].reshape(-1, 4)
    regular = 0
    singular = 0
    for block in grouped:
        if block.size < 2:
            continue
        diff = np.abs(np.diff(block)).sum()
        flipped = np.abs(np.diff(block ^ 1)).sum()
        if diff < flipped:
            regular += 1
        else:
            singular += 1
    total = max(1, regular + singular)
    imbalance = abs(regular - singular) / total
    return {
        "module": "rs_analysis",
        "score": float(min(1.0, imbalance)),
        "details": {"regular": regular, "singular": singular, "imbalance": imbalance},
    }
