import os
import json
from app.research.report_generator import ReportGenerator


def test_stability_blocks_promotion(tmp_path, monkeypatch):
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    # create a WFV artifact where mlp is top but unstable
    wfv = [
        {"model": "mlp", "average_accuracy": 0.49982980612697947, "folds": 4},
        {"model": "lightgbm", "average_accuracy": 0.49364547876276454, "folds": 4},
    ]
    wfv_path = artifacts_dir / "model_family_benchmark_wfv.json"
    with open(wfv_path, "w", encoding="utf-8") as f:
        json.dump(wfv, f)

    # create mlp stability artifact disallowing production
    mlp_stab = {
        "mean_accuracy": 0.49982980612697947,
        "std_accuracy": 0.03907987732203459,
        "production_allowed": False,
    }
    with open(artifacts_dir / "mlp_stability.json", "w", encoding="utf-8") as f:
        json.dump(mlp_stab, f)

    # run report generator from tmp cwd
    monkeypatch.chdir(tmp_path)
    rg = ReportGenerator()
    rg.generate([])

    promotion_path = artifacts_dir / "promotion_decision.json"
    assert promotion_path.exists()
    with open(promotion_path, "r", encoding="utf-8") as f:
        promotion = json.load(f)

    # production should be lightgbm because mlp was blocked by stability
    assert promotion.get("production") == ["lightgbm"]
    # benchmark should still contain top_k models (mlp included)
    assert "mlp" in promotion.get("benchmark", [])
