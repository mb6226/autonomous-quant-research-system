from app.research.promotion_engine import classify_walk_forward_results


def test_promotion_engine_v2_high_std():
    # Top model has highest accuracy but high std -> should not be production
    data = [
        {"model": "mlp", "average_accuracy": 0.60, "std_accuracy": 0.05, "folds": 4},
        {"model": "lightgbm", "average_accuracy": 0.59, "std_accuracy": 0.01, "folds": 4},
    ]
    res = classify_walk_forward_results(data, top_k=2, std_threshold=0.02)
    assert res["production"] == ["lightgbm"]
    assert "mlp" in res["benchmark"]
    assert res["details"]["mlp"]["eligible_for_production"] is False


def test_promotion_engine_v2_low_std():
    # Top model has highest accuracy and low std -> should be production
    data = [
        {"model": "mlp", "average_accuracy": 0.60, "std_accuracy": 0.01, "folds": 4},
        {"model": "lightgbm", "average_accuracy": 0.59, "std_accuracy": 0.01, "folds": 4},
    ]
    res = classify_walk_forward_results(data, top_k=2, std_threshold=0.02)
    assert res["production"] == ["mlp"]
    assert res["details"]["mlp"]["eligible_for_production"] is True
