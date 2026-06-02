Cross Market Validation
=======================

Overview
--------
This validation runs Walk-Forward Validation for each benchmark model across multiple markets and summarizes per-market and overall performance.

Markets
-------
- BTCUSDT
- EURUSD
- XAUUSD
- USOIL
- US30

Timeframe: 1d
Target: classification_up_down_5

Per-Market Results
------------------
Results are persisted to `artifacts/cross_market_validation.json`. Each model maps to per-market metrics:

```
{
  "model": {
    "BTCUSDT": {"avg_accuracy": ..., "avg_precision": ..., "avg_recall": ..., "avg_f1": ...},
    "EURUSD": {...},
    ...,
    "overall_average_accuracy": ...
  }
}
```

Overall Ranking
---------------
Ranking is saved to `artifacts/cross_market_ranking.json`, sorted by `overall_average_accuracy`.

Champion
--------
The champion is the top entry in `cross_market_ranking.json`.

Observations
------------
- Use `artifacts/cross_market_validation.json` to inspect per-market weaknesses.
- If a model's overall average is driven down by one market, investigate dataset quality and feature coverage for that market.

Questions
---------
- Does LightGBM remain champion?
- Does MLP generalize across markets?
- Does any model collapse on a specific market?
