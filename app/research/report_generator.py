import json
import os
from datetime import datetime
from typing import Any

from app.research.auto_leaderboard import AutoLeaderboard


class ReportGenerator:
    def __init__(self):
        pass

    def _load_feature_ranking(self) -> list | None:
        path = os.path.join(os.getcwd(), "artifacts", "feature_ranking.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("ranking") if isinstance(data, dict) else data
        except Exception:
            return None

    def generate(self, research_run_result: Any) -> str:
        # research_run_result can be a dataclass with attributes or a list of dicts
        out_dir = os.path.join(os.getcwd(), "artifacts")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "research_report.md")

        # normalize results list
        results = []
        total = 0
        successful = 0
        failed = 0
        leaderboard = None

        # If user passed a ResearchRunResult-like object
        if hasattr(research_run_result, "results"):
            results = list(research_run_result.results)
            total = getattr(research_run_result, "total_experiments", len(results))
            successful = getattr(research_run_result, "successful_experiments", sum(1 for r in results if getattr(r, "accuracy", None) is not None))
            failed = getattr(research_run_result, "failed_experiments", total - successful)
            leaderboard = getattr(research_run_result, "leaderboard", None)
        # If passed a plain list (from JSON)
        elif isinstance(research_run_result, list):
            for item in research_run_result:
                results.append(item)
            total = len(results)
            successful = sum(1 for r in results if r.get("accuracy") is not None)
            failed = total - successful
            leaderboard = None
        else:
            # try to treat as path to JSON
            try:
                with open(str(research_run_result), "r", encoding="utf-8") as f:
                    results = json.load(f)
                total = len(results)
                successful = sum(1 for r in results if r.get("accuracy") is not None)
                failed = total - successful
            except Exception:
                # fallback empty
                results = []

        # prepare leaderboard entries
        top_list = []
        if leaderboard is not None and isinstance(leaderboard, AutoLeaderboard):
            top_list = leaderboard.top(10)
        else:
            # results may be list of dicts or objects
            def acc_of(r):
                if isinstance(r, dict):
                    return r.get("accuracy")
                return getattr(r, "accuracy", None)

            sorted_results = sorted(results, key=lambda r: (acc_of(r) is not None, acc_of(r) or 0), reverse=True)
            top_list = sorted_results[:10]

        # load feature ranking
        feature_ranking = self._load_feature_ranking()

        # write markdown
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("# Research Report\n\n")
            f.write("## Summary\n\n")
            f.write(f"- Total Experiments: {total}\n")
            f.write(f"- Successful Experiments: {successful}\n")
            f.write(f"- Failed Experiments: {failed}\n\n")

            f.write("## Best Result\n\n")
            if len(top_list) > 0:
                best = top_list[0]
                if isinstance(best, dict):
                    f.write(f"- Market: {best.get('market')}\n")
                    f.write(f"- Model: {best.get('model')}\n")
                    f.write(f"- Target: {best.get('target')}\n")
                    f.write(f"- Accuracy: {best.get('accuracy')}\n\n")
                else:
                    f.write(f"- Market: {getattr(best, 'market', '')}\n")
                    f.write(f"- Model: {getattr(best, 'model', '')}\n")
                    f.write(f"- Target: {getattr(best, 'target', '')}\n")
                    f.write(f"- Accuracy: {getattr(best, 'accuracy', None)}\n\n")
            else:
                f.write("No results available.\n\n")

            f.write("## Leaderboard\n\n")
            f.write("| Rank | Market | Model | Target | Accuracy |\n")
            f.write("|---:|---|---|---|---:|\n")
            for i, r in enumerate(top_list, start=1):
                if isinstance(r, dict):
                    f.write(f"| {i} | {r.get('market')} | {r.get('model')} | {r.get('target')} | {r.get('accuracy')} |\n")
                else:
                    f.write(f"| {i} | {getattr(r,'market','')} | {getattr(r,'model','')} | {getattr(r,'target','')} | {getattr(r,'accuracy',None)} |\n")

            f.write("\n## Feature Selection\n\n")
            if feature_ranking:
                f.write("Top features (feature, delta):\n\n")
                for i, item in enumerate(feature_ranking[:20], start=1):
                    if isinstance(item, list) or isinstance(item, tuple):
                        f.write(f"{i}. {item[0]} — {item[1]}\n")
                    elif isinstance(item, dict):
                        f.write(f"{i}. {item.get('feature')} — {item.get('delta')}\n")
            else:
                f.write("No feature ranking available.\n")

            f.write("\n## Notes\n\n")
            f.write(f"- Generation timestamp: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"- Results source: {"in-memory" if hasattr(research_run_result, 'results') else 'artifacts/research_results.json'}\n")

        return out_path
