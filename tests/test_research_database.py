from app.research.research_database import (
    ResearchDatabase,
)

db = ResearchDatabase()

db.save(
    "btc_rf_v1",
    {
        "accuracy": 0.61,
        "rows": 2344,
    },
)

result = db.load(
    "btc_rf_v1"
)

print(result)
