import json
from pathlib import Path


DB_DIR = Path(
    "data/research"
)


class ResearchDatabase:

    def save(
        self,
        experiment_name: str,
        result: dict,
    ):

        DB_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            DB_DIR
            / f"{experiment_name}.json"
        )

        with open(
            path,
            "w",
        ) as f:

            json.dump(
                result,
                f,
                indent=2,
            )

    def load(
        self,
        experiment_name: str,
    ):

        path = (
            DB_DIR
            / f"{experiment_name}.json"
        )

        with open(path) as f:
            return json.load(f)
