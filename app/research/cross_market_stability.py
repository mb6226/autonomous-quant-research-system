import json
import os
from typing import List, Dict, Any

import numpy as np

from app.research.walk_forward_validator import WalkForwardValidator
from app.research.cross_market_validator import CrossMarketValidator

from app.models.extra_trees_classifier import ExtraTreesClassifierModel
from app.models.lightgbm_classifier import LightGBMClassifierModel
from app.models.mlp_classifier import MLPClassifierModel


MODEL_CLASSES = {
    "extra_trees": ExtraTreesClassifierModel,
    "lightgbm": LightGBMClassifierModel,
    "mlp": MLPClassifierModel,
}


class CrossMarketStability:
    def __init__(self, seeds: List[int], markets: List[str], timeframe: str = "1d"):
        self.seeds = seeds
        self.markets = markets
        self.timeframe = timeframe
        self.cross_validator = CrossMarketValidator(allow_sampling=False)
        self.wfv = WalkForwardValidator()

    def run(self, models: List[str], out_path: str = None) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}

        for model_name in models:
            seed_results = []
            for s in self.seeds:
                per_market_accs = []
                for m in self.markets:
                    try:
                        X, y = self.cross_validator._load_and_prepare(m, self.timeframe, "classification_up_down_5")
                    except Exception as e:
                        per_market_accs.append(None)
                        continue

                    if X is None or len(X) == 0:
                        per_market_accs.append(None)
                        continue

                    cls = MODEL_CLASSES.get(model_name)
                    if cls is None:
                        per_market_accs.append(None)
                        continue

                    # instantiate model bound to seed where supported
                    try:
                        model_factory = lambda seed=s, C=cls: C(random_state=seed)
                        wfv = self.wfv.run(model_factory, X, y)
                        per_market_accs.append(wfv.avg_accuracy)
                    except Exception:
                        per_market_accs.append(None)

                # compute overall average across markets for this seed (skip None)
                vals = [v for v in per_market_accs if v is not None]
                overall = float(np.mean(vals)) if vals else None
                seed_results.append({"seed": s, "overall_average_accuracy": overall, "per_market": per_market_accs})

            accs = np.array([r["overall_average_accuracy"] for r in seed_results], dtype=float)
            mean_acc = float(np.nanmean(accs))
            std_acc = float(np.nanstd(accs, ddof=0))

            summary[model_name] = {
                "seeds": self.seeds,
                "seed_results": seed_results,
                "mean_accuracy": mean_acc,
                "std_accuracy": std_acc,
            }

        if out_path:
            try:
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2)
            except Exception:
                pass

        return summary


def quick_run():
    seeds = [42, 123, 456, 789, 999]
    markets = ["BTCUSDT", "EURUSD", "XAUUSD", "USOIL", "US30"]
    models = ["extra_trees", "lightgbm", "mlp"]
    s = CrossMarketStability(seeds, markets)
    out = s.run(models, out_path=os.path.join(os.getcwd(), "artifacts", "cross_market_stability.json"))
    return out
