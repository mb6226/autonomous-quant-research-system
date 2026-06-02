from typing import List, Dict, Any
import json


def classify_walk_forward_results(wfv_results: List[Dict[str, Any]], top_k: int = 5) -> Dict[str, List[str]]:
    """Classify models into Production, Benchmark, Experimental, Archived.

    Input: list of dicts with at least: 'model' and either 'average_accuracy' or 'accuracy'.
    Rules (V1):
      - Production: top model by average accuracy
      - Benchmark: top_k models
      - Experimental: models with insufficient validation (folds missing or <1 or missing accuracy)
      - Archived: all other models

    Returns a dict with keys: 'production','benchmark','experimental','archived'.
    """
    if not isinstance(wfv_results, list):
        raise ValueError("wfv_results must be a list of model result dicts")

    # Normalize entries and detect validated vs unvalidated
    normalized = []
    for entry in wfv_results:
        name = entry.get("model")
        if name is None:
            continue
        acc = entry.get("average_accuracy")
        if acc is None:
            acc = entry.get("accuracy")
        folds = int(entry.get("folds", 0) or 0)
        validated = (acc is not None) and (folds >= 1)
        normalized.append({"model": name, "accuracy": acc, "folds": folds, "validated": validated})

    # Experimental = models without sufficient validation
    experimental = [e["model"] for e in normalized if not e["validated"]]

    # Sort validated models by accuracy desc (None -> -inf)
    validated_models = [e for e in normalized if e["validated"]]
    validated_models.sort(key=lambda x: (x["accuracy"] if x["accuracy"] is not None else float("-inf")), reverse=True)

    ranked = [e["model"] for e in validated_models]

    production = [ranked[0]] if ranked else []
    benchmark = ranked[:top_k]

    # Archived = validated models outside benchmark
    archived = [m for m in ranked if m not in benchmark]

    return {
        "production": production,
        "benchmark": benchmark,
        "experimental": experimental,
        "archived": archived,
    }


def load_results_from_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r") as f:
        return json.load(f)


def write_promotion_to_file(promotion: Dict[str, List[str]], path: str) -> None:
    with open(path, "w") as f:
        json.dump(promotion, f, indent=2)
