import json
from pathlib import Path

manifest_dir = Path(
    "data/manifests"
)

for file in sorted(
    manifest_dir.glob("*.json")
):

    with open(file) as f:
        data = json.load(f)

    print(
        f"{data['symbol']} "
        f"{data['timeframe']} "
        f"rows={data['rows']}"
    )
