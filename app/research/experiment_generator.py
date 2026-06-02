from dataclasses import dataclass
from typing import List, Iterable


@dataclass
class Experiment:
    market: str
    model: str
    target: str
    feature_set: str


class ExperimentGenerator:

    def __init__(
        self,
        markets: Iterable[str],
        models: Iterable[str],
        targets: Iterable[str],
        feature_sets: Iterable[str],
    ):
        self.markets = list(markets)
        self.models = list(models)
        self.targets = list(targets)
        self.feature_sets = list(feature_sets)

    def generate(self) -> List[Experiment]:
        experiments: List[Experiment] = []
        for m in self.markets:
            for mod in self.models:
                for t in self.targets:
                    for f in self.feature_sets:
                        experiments.append(
                            Experiment(
                                market=m,
                                model=mod,
                                target=t,
                                feature_set=f,
                            )
                        )
        return experiments
