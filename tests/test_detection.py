from app.detection.decision import evaluate_decision
from app.detection.engine import run_detection_pipeline


def test_pipeline_returns_all_modules(tmp_path):
    from PIL import Image

    image_path = tmp_path / "sample.png"
    Image.new("RGB", (16, 16), color=(120, 80, 200)).save(image_path)
    out = run_detection_pipeline(image_path)
    modules = [item["module"] for item in out["results"]]
    assert out["preprocessing"]["conversion"] == "RGB"
    assert set(modules) == {
        "chi_square",
        "rs_analysis",
        "histogram",
        "texture",
        "transform",
        "ai_detection",
        "anomaly",
    }


def test_decision_classification_bounds():
    decision = evaluate_decision(
        [
            {"module": "chi_square", "score": 0.1},
            {"module": "rs_analysis", "score": 0.1},
            {"module": "histogram", "score": 0.1},
            {"module": "texture", "score": 0.1},
            {"module": "transform", "score": 0.1},
            {"module": "ai_detection", "score": 0.1},
            {"module": "anomaly", "score": 0.1},
        ]
    )
    assert decision["classification"] == "benign"
    assert 0 <= decision["risk_score"] <= 1
