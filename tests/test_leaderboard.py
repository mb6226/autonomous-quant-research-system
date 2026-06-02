from app.research.leaderboard import (
    Leaderboard,
)

results = [
    {
        "model": "rf",
        "r2": 0.12,
    },
    {
        "model": "xgb",
        "r2": 0.25,
    },
    {
        "model": "lgbm",
        "r2": 0.18,
    },
]

ranked = (
    Leaderboard()
    .rank(results)
)

for row in ranked:
    print(row)
