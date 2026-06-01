from app.data.manifests.manifest_store import (
    ManifestStore,
)

ManifestStore().save(
    "btcusdt_1d",
    {
        "symbol": "BTCUSDT",
        "rows": 1000,
    },
)

print("OK")
