import json
from pathlib import Path

MANIFEST_DIR = Path(
    "data/manifests"
)

class ManifestStore:

    def save(
        self,
        name: str,
        payload: dict,
    ):

        MANIFEST_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            MANIFEST_DIR
            / f"{name}.json"
        )

        with open(
            path,
            "w",
        ) as f:

            json.dump(
                payload,
                f,
                indent=2,
            )
