import os
import json

from app.research.promotion_engine import classify_walk_forward_results, load_results_from_file
from app.research.report_generator import ReportGenerator


def test_promotion_engine_v2_loads_and_basic_call():
    # ensure module loads and basic call works
    res = classify_walk_forward_results([{"model": "m", "average_accuracy": 0.5, "folds": 1}], top_k=1)
    assert isinstance(res, dict)


def test_promotion_engine_v1_compatibility():
    # replicate the V1 basic behavior test
    mock_results = [
        {"model": "lightgbm", "average_accuracy": 0.49364547876276454, "folds": 4},
        {"model": "catboost", "average_accuracy": 0.4914671821814415, "folds": 4},
        {"model": "xgboost", "average_accuracy": 0.4893212594346603, "folds": 4},
        {"model": "random_forest", "average_accuracy": 0.473185215332248, "folds": 4},
        {"model": "extra_trees", "average_accuracy": 0.4678157836317892, "folds": 4},
    ]

    promotion = classify_walk_forward_results(mock_results, top_k=5)
    assert len(promotion["production"]) == 1
    assert promotion["production"][0] == "lightgbm"
    assert set(promotion["benchmark"]) == {"lightgbm", "catboost", "xgboost", "random_forest", "extra_trees"}
    assert promotion["experimental"] == []
    assert promotion["archived"] == []


def test_promotion_engine_v2_expected_cases():
    data = [
        {"model": "mlp", "average_accuracy": 0.60, "std_accuracy": 0.05, "folds": 4},
        {"model": "lightgbm", "average_accuracy": 0.59, "std_accuracy": 0.01, "folds": 4},
    ]
    res = classify_walk_forward_results(data, top_k=2, std_threshold=0.02)
    assert res["production"] == ["lightgbm"]
    assert "mlp" in res["benchmark"]
    assert res["details"]["mlp"]["eligible_for_production"] is False


def test_report_generator_loads_promotion_decision_and_expected_state():
    # Ensure promotion_decision.json exists and can be loaded by ReportGenerator
    promotion_path = os.path.join(os.getcwd(), "artifacts", "promotion_decision.json")
    assert os.path.exists(promotion_path), "promotion_decision.json not found in artifacts"

    # Load and assert expected final state (production + benchmark)
    with open(promotion_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    final = data.get("final") or data
    production = final.get("production", [])
    benchmark = final.get("benchmark", [])
    details = final.get("details", {})

    # If the promotion artifact already contains the model-family decision, assert directly
    if "mlp" in benchmark:
        assert production == ["lightgbm"], "Expected production to be ['lightgbm']"
        expected_benchmark = ["mlp", "lightgbm", "catboost", "xgboost", "random_forest"]
        for m in expected_benchmark:
            assert m in benchmark, f"Expected {m} in benchmark"
        assert "mlp" in details
        assert details["mlp"].get("eligible_for_production") is False
    else:
        # Fallback: regenerate using model_family_benchmark_wfv.json and ensure expected state
        model_family_path = os.path.join(os.getcwd(), "artifacts", "model_family_benchmark_wfv.json")
        assert os.path.exists(model_family_path), "model_family_benchmark_wfv.json missing for fallback check"
        mf = load_results_from_file(model_family_path)
        # classify using stability threshold 0.02
        computed = classify_walk_forward_results(mf, top_k=5, std_threshold=0.02)
        assert computed["production"] == ["lightgbm"]
        for m in ["mlp", "lightgbm", "catboost", "xgboost", "random_forest"]:
            assert m in computed["benchmark"]
        assert computed["details"]["mlp"]["eligible_for_production"] is False

    # Finally, ensure ReportGenerator can generate a report using the promotion_decision as input
    rg = ReportGenerator()
    out = rg.generate(promotion_path)
    assert os.path.exists(out)
