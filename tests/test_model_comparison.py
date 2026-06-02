from app.research.model_comparison import (
    ModelComparison,
)

winner = (
    ModelComparison()
    .best(
        [
            {
                "model": "xgb",
                "r2": 0.25,
            },
            {
                "model": "lgbm",
                "r2": 0.18,
            },
        ]
    )
)

print(winner)
