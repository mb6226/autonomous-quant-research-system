from typing import List, Dict, Any
import os
import json
import numpy as np

from app.research.walk_forward_validator import WalkForwardValidator
from app.models.mlp_classifier import MLPClassifierModel


class StabilityResult:
    def __init__(self):
        self.seed_results: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {"seed_results": self.seed_results}


class StabilityValidator:
    def __init__(self, seeds: List[int] = None):
        self.seeds = seeds or [42, 123, 456, 789, 999]
        self.validator = WalkForwardValidator()

    def run_mlp_stability(self, X, y, out_path: str = None) -> Dict[str, Any]:
        results = []
        for s in self.seeds:
            # create model factory bound to seed
            model_factory = lambda seed=s: MLPClassifierModel(random_state=seed)
            wfv = self.validator.run(model_factory, X, y)
            results.append({
                "seed": s,
                "accuracy": wfv.avg_accuracy,
                "precision": wfv.avg_precision,
                "recall": wfv.avg_recall,
                "f1": wfv.avg_f1,
                "folds": len(wfv.folds),
            })

        accs = np.array([r["accuracy"] for r in results], dtype=float)
        precs = np.array([r["precision"] for r in results], dtype=float)
        recs = np.array([r["recall"] for r in results], dtype=float)
        f1s = np.array([r["f1"] for r in results], dtype=float)

        summary = {
            "seeds": self.seeds,
            "seed_results": results,
            "mean_accuracy": float(np.nanmean(accs)),
            "std_accuracy": float(np.nanstd(accs, ddof=0)),
            "mean_precision": float(np.nanmean(precs)),
            "std_precision": float(np.nanstd(precs, ddof=0)),
            "mean_recall": float(np.nanmean(recs)),
            "std_recall": float(np.nanstd(recs, ddof=0)),
            "mean_f1": float(np.nanmean(f1s)),
            "std_f1": float(np.nanstd(f1s, ddof=0)),
        }

        # Promotion rule V1: if std_accuracy > 0.02 then cannot be Production
        summary["production_allowed"] = summary["std_accuracy"] <= 0.02

        if out_path:
            try:
                out_dir = os.path.dirname(out_path)
                if out_dir:
                    os.makedirs(out_dir, exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2)
            except Exception:
                pass

        return summary
