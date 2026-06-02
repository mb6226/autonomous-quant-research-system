Model Promotion Policy (V1)
===========================

Purpose
-------
Automate model status assignment using Walk-Forward Validation (WFV) results. This policy ensures promotion decisions use robust, time-aware metrics.

Status Buckets
--------------
- Production: Single model used for serving/production. Must be the top-ranked model by average WFV accuracy.
- Benchmark: Top N validated models (default N=5). These models are tracked and compared in periodic benchmarks.
- Experimental: New or unvalidated models without sufficient WFV folds.
- Archived: Validated models that fall outside the benchmark set.

Transition Rules (V1)
---------------------
- On each benchmark run (WFV), sort validated models by `average_accuracy` desc.
- Assign `production` to the top-ranked model.
- Assign `benchmark` to the top N models.
- Any validated model not in `benchmark` is `archived`.
- Any model lacking validation folds or accuracy is `experimental`.

Operational Notes
-----------------
- Single-split metrics are informational only; promotion decisions must use WFV metrics.
- Promotion runs should be persisted (artifact) and recorded in the research database.
- Promotion actions should be performed only after human review for major changes.

Stability Rule (V2)
--------------------
- For stability-sensitive models (e.g., neural nets), a stability validation artifact may be produced at `artifacts/{model}_stability.json`.
- When present, the Promotion Engine will consult this artifact. A model is only eligible for `production` if:
	- `production_allowed` is `true` in the stability artifact, or
	- `std_accuracy` exists and is <= 0.02.
- If the top-ranked model fails the stability gate it will be excluded from `production` selection; the engine will pick the next highest-ranked eligible model. The model may still appear in `benchmark` for tracking and further analysis.

Promotion Artifact
------------------
The promotion engine produces a persistent artifact at `artifacts/promotion_decision.json` with the following structure:

```
{
	"production": ["lightgbm"],
	"benchmark": ["lightgbm","catboost","xgboost"],
	"experimental": [],
	"archived": []
}
```

Decision Flow
-------------
- After a WFV benchmark run, the `ReportGenerator` will load `artifacts/tree_model_benchmark_wfv.json` and invoke the Promotion Engine.
- The generated `promotion_decision.json` is appended to the research report and persisted as a first-class artifact.
- Teams should treat this artifact as the canonical promotion suggestion and follow human review for final promotions.

Stability Gate
--------------
Promotion decisions now include a stability gate. For a model to be eligible for Production it must:

- Be the top-ranked model by average WFV accuracy, and
- Have `std_accuracy` less than or equal to the configured stability threshold (default 0.02).

If the top-ranked model fails the stability gate, the Promotion Engine will select the next highest-ranked model that satisfies the gate. All top-ranked models remain in the Benchmark set and detailed per-model metrics are included in the promotion artifact under `details`.
