from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass
class PreprocessResult:
    frames: list[np.ndarray]
    normalized: np.ndarray
    mode: str


def preprocess(path: Path) -> PreprocessResult:
    with Image.open(path) as img:
        frame = np.array(img.convert("RGB"))
    return PreprocessResult(frames=[frame], normalized=frame.astype(np.float32) / 255.0, mode="image")
