from app.research.promotion_engine import classify_walk_forward_results


def test_promotion_engine_basic():
    mock_results = [
        {"model": "lightgbm", "average_accuracy": 0.49364547876276454, "folds": 4},
        {"model": "catboost", "average_accuracy": 0.4914671821814415, "folds": 4},
        {"model": "xgboost", "average_accuracy": 0.4893212594346603, "folds": 4},
        {"model": "random_forest", "average_accuracy": 0.473185215332248, "folds": 4},
        {"model": "extra_trees", "average_accuracy": 0.4678157836317892, "folds": 4},
    ]

    promotion = classify_walk_forward_results(mock_results, top_k=5)

    # Exactly one production model and it's the top-ranked
    assert len(promotion["production"]) == 1
    assert promotion["production"][0] == "lightgbm"

    # Benchmark contains all ranked models (top_k)
    assert set(promotion["benchmark"]) == {"lightgbm", "catboost", "xgboost", "random_forest", "extra_trees"}
    assert len(promotion["benchmark"]) == 5

    # No experimental or archived in this input
    assert promotion["experimental"] == []
    assert promotion["archived"] == []
