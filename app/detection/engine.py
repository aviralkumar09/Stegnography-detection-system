from pathlib import Path

from .ai_detection import ai_detection
from .anomaly import anomaly_detection
from .histogram import histogram_analysis
from .preprocessing import preprocess
from .rs_analysis import rs_analysis
from .statistical import chi_square_analysis
from .texture import texture_analysis
from .transform import transform_analysis

MODULE_SEQUENCE = [
    chi_square_analysis,
    rs_analysis,
    histogram_analysis,
    texture_analysis,
    transform_analysis,
    ai_detection,
    anomaly_detection,
]


def run_detection_pipeline(file_path: Path) -> dict:
    prep = preprocess(file_path)
    frame = prep.frames[0]
    return {
        "preprocessing": {
            "mode": prep.mode,
            "frame_count": len(prep.frames),
            "shape": list(frame.shape),
            "normalization": "float32_[0,1]",
            "conversion": "RGB",
            "frame_extraction": "single_frame_for_image",
        },
        "results": [fn(frame) for fn in MODULE_SEQUENCE],
    }
