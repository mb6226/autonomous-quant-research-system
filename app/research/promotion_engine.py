from typing import List, Dict, Any, Optional
import json
import os


def _production_allowed_from_artifact(model_name: str, threshold: float = 0.02) -> bool:
    """Check artifacts/{model}_stability.json for a production_allowed flag.

    If the artifact exists and contains `production_allowed`, use it.
    If it contains `std_accuracy`, apply the threshold as a fallback.
    If the artifact is missing or cannot be read, assume production is allowed.
    """
    """
    Environment override:
      - If `AQRS_IGNORE_STABILITY_ARTIFACTS` is set to a truthy value, skip artifact checks and allow production.
    """
    try:
        # testing/runtime override to ignore stability artifacts
        if os.environ.get("AQRS_IGNORE_STABILITY_ARTIFACTS") in ("1", "true", "True"):
            return True
        path = os.path.join(os.getcwd(), "artifacts", f"{model_name}_stability.json")
        if not os.path.exists(path):
            return True
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            if "production_allowed" in data:
                return bool(data.get("production_allowed"))
            if "std_accuracy" in data:
                try:
                    return float(data.get("std_accuracy", 0.0)) <= float(threshold)
                except Exception:
                    return True
    except Exception:
        return True
    return True


def classify_walk_forward_results(
    wfv_results: List[Dict[str, Any]], top_k: int = 5, std_threshold: float = 0.02
) -> Dict[str, Any]:
    """Classify models into Production, Benchmark, Experimental, Archived and include details.

    New rules (V2):
      - Production: highest-ranked validated model by average_accuracy that also has std_accuracy <= std_threshold (if std available)
      - If the top-ranked model fails the stability gate, pick the next highest that passes.
      - Benchmark: top_k models by average_accuracy (regardless of stability)
      - Experimental: models without sufficient validation (folds missing or <1 or missing accuracy)
      - Archived: validated models outside benchmark

    The returned dict includes lists and a `details` mapping with per-model metrics and
    `eligible_for_production` flag.
    """
    if not isinstance(wfv_results, list):
        raise ValueError("wfv_results must be a list of model result dicts")

    normalized: List[Dict[str, Any]] = []
    for entry in wfv_results:
        name = entry.get("model")
        if name is None:
            continue
        acc = entry.get("average_accuracy")
        if acc is None:
            acc = entry.get("accuracy")
        folds = int(entry.get("folds", 0) or 0)
        std_acc: Optional[float] = None
        if "std_accuracy" in entry:
            try:
                std_acc = float(entry.get("std_accuracy"))
            except Exception:
                std_acc = None
        elif "std" in entry:
            try:
                std_acc = float(entry.get("std"))
            except Exception:
                std_acc = None

        validated = (acc is not None) and (folds >= 1)
        normalized.append({
            "model": name,
            "accuracy": acc,
            "folds": folds,
            "std_accuracy": std_acc,
            "validated": validated,
        })

    experimental = [e["model"] for e in normalized if not e["validated"]]

    validated_models = [e for e in normalized if e["validated"]]
    validated_models.sort(key=lambda x: (x["accuracy"] if x["accuracy"] is not None else float("-inf")), reverse=True)

    details: Dict[str, Dict[str, Any]] = {}
    for e in validated_models:
        model_name = e["model"]
        std_val = e.get("std_accuracy")
        eligible = True if (std_val is None) else (std_val <= std_threshold)
        artifact_allowed = _production_allowed_from_artifact(model_name, threshold=std_threshold)
        details[model_name] = {
            "average_accuracy": e["accuracy"],
            "std_accuracy": std_val,
            "folds": e["folds"],
            "eligible_for_production": bool(eligible and artifact_allowed),
        }

    ranked = [e["model"] for e in validated_models]

    production: List[str] = []
    for name in ranked:
        d = details.get(name, {})
        if d.get("eligible_for_production", True):
            production = [name]
            break

    benchmark = ranked[:top_k]
    archived = [m for m in ranked if m not in benchmark]

    return {
        "production": production,
        "benchmark": benchmark,
        "experimental": experimental,
        "archived": archived,
        "details": details,
    }


def load_results_from_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_promotion_to_file(promotion: Dict[str, Any], path: str) -> None:
    out = {k: promotion.get(k, []) for k in ("production", "benchmark", "experimental", "archived")}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
