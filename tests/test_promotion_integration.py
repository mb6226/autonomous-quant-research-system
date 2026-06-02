import os
import json
from app.research.report_generator import ReportGenerator


def test_promotion_integration(tmp_path, monkeypatch):
    # prepare fake artifacts dir
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    # create a fake WFV benchmark artifact
    wfv = [
        {"model": "lightgbm", "average_accuracy": 0.49364547876276454, "folds": 4},
        {"model": "catboost", "average_accuracy": 0.4914671821814415, "folds": 4},
        {"model": "xgboost", "average_accuracy": 0.4893212594346603, "folds": 4},
    ]
    wfv_path = artifacts_dir / "tree_model_benchmark_wfv.json"
    with open(wfv_path, "w") as f:
        json.dump(wfv, f)

    # monkeypatch cwd to tmp_path so ReportGenerator writes to tmp artifacts
    monkeypatch.chdir(tmp_path)

    rg = ReportGenerator()
    out = rg.generate([])

    # assert promotion_decision.json exists and has correct production
    promotion_path = tmp_path / "artifacts" / "promotion_decision.json"
    assert promotion_path.exists()
    with open(promotion_path, "r") as f:
        promotion = json.load(f)

    assert "production" in promotion
    assert len(promotion["production"]) == 1
    assert promotion["production"][0] == "lightgbm"
