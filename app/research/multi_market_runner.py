from dataclasses import dataclass
from typing import List, Any
import json
import os

from app.research.experiment_generator import Experiment
from app.research.experiment_runner import ExperimentRunner, ExperimentResultSimple
from app.research.auto_leaderboard import AutoLeaderboard


@dataclass
class ResearchRunResult:
    total_experiments: int
    successful_experiments: int
    failed_experiments: int
    leaderboard: AutoLeaderboard
    results: List[ExperimentResultSimple]


class MultiMarketRunner:
    def __init__(self):
        # production runs should not sample by default
        self.runner = ExperimentRunner(allow_sampling=False)
        self.leaderboard = AutoLeaderboard()

    def run(self, experiments: List[Experiment]) -> ResearchRunResult:
        results: List[ExperimentResultSimple] = []
        successful = 0
        failed = 0

        for exp in experiments:
            try:
                res = self.runner.run(exp)
                results.append(res)
                self.leaderboard.add(res)
                if getattr(res, "accuracy", None) is not None:
                    successful += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

        # persist simplified results
        out_dir = os.path.join(os.getcwd(), "artifacts")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "research_results.json")
        serial = []
        for r in results:
            serial.append({
                "market": r.market,
                "model": r.model,
                "target": r.target,
                "accuracy": r.accuracy,
            })
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(serial, f, indent=2)

        return ResearchRunResult(
            total_experiments=len(experiments),
            successful_experiments=successful,
            failed_experiments=failed,
            leaderboard=self.leaderboard,
            results=results,
        )
