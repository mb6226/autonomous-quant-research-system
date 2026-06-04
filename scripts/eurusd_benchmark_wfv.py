#!/usr/bin/env python3
"""Run Walk-Forward Validation benchmarks for EURUSD on multiple timeframes.

Produces:
- artifacts/eurusd_multitimeframe_benchmark.json
- artifacts/eurusd_promotion_decision.json
- docs/EURUSD_MULTITIMEFRAME_BENCHMARK.md
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

from app.research.walk_forward_validator import WalkForwardValidator
from app.features.feature_factory import FeatureFactory
from app.targets.target_factory import TargetFactory
from app.research.experiment_runner import ExperimentRunner
from app.research.promotion_engine import classify_walk_forward_results, write_promotion_to_file

ROOT = Path('.').resolve()
ART = ROOT / 'artifacts'
ART.mkdir(parents=True, exist_ok=True)
DOCS = ROOT / 'docs'
DOCS.mkdir(parents=True, exist_ok=True)

MODELS = ['lightgbm','catboost','xgboost','random_forest','extra_trees','mlp']
TIMEFRAMES = ['15m','30m','1h']
TARGET = 'classification_up_down_5'

def load_and_prepare(market, timeframe):
    path = ROOT / 'data' / 'raw' / market / f"{timeframe}.parquet"
    df = pd.read_parquet(path)
    ff = FeatureFactory()
    tf = TargetFactory()
    df = ff.build(df)
    y = tf.classification_up_down(df, periods=5)
    # select numeric features
    features = [c for c in df.columns if str(df[c].dtype) in ['float64','int64','bool']]
    if 'target' in features:
        features.remove('target')
    X = df[features]
    # dropna
    mask = X.notna().all(axis=1) & y.notna()
    X = X.loc[mask].reset_index(drop=True)
    y = y.loc[mask].reset_index(drop=True)
    return X, y

def run_benchmarks():
    runner = ExperimentRunner(allow_sampling=False)
    validator = WalkForwardValidator()
    results = {}
    per_model_agg = {m: [] for m in MODELS}

    for tf in TIMEFRAMES:
        X, y = load_and_prepare('EURUSD', tf)
        tf_results = []
        for m in MODELS:
            # model factory returns new instance
            model_factory = (lambda mn=m: runner._get_model_impl(mn))
            wfv = validator.run(model_factory, X, y)
            # compute std across fold accuracies
            fold_accs = [f.accuracy for f in wfv.folds if f.accuracy is not None]
            avg = wfv.avg_accuracy
            std = float(np.std(fold_accs)) if fold_accs else None
            entry = {'model': m, 'average_accuracy': avg, 'std_accuracy': std, 'folds': len(fold_accs)}
            tf_results.append(entry)
            if avg is not None:
                per_model_agg[m].append((avg, std))
        results[tf] = tf_results

    # save per-timeframe results
    out_path = ART / 'eurusd_multitimeframe_benchmark.json'
    out_path.write_text(json.dumps(results, indent=2))

    # aggregate across timeframes for promotion engine
    agg_list = []
    for m in MODELS:
        vals = [v[0] for v in per_model_agg[m] if v[0] is not None]
        stds = [v[1] for v in per_model_agg[m] if v[1] is not None]
        avg_all = float(np.mean(vals)) if vals else None
        std_all = float(np.std(vals)) if vals else None
        folds = sum([1 for v in per_model_agg[m] if v[0] is not None]) * len(validator.train_stops)
        agg_list.append({'model': m, 'average_accuracy': avg_all, 'std_accuracy': std_all, 'folds': folds})

    promo = classify_walk_forward_results(agg_list, top_k=5)
    promo_path = ART / 'eurusd_promotion_decision.json'
    write_promotion_to_file(promo, str(promo_path))

    # write docs
    md = DOCS / 'EURUSD_MULTITIMEFRAME_BENCHMARK.md'
    lines = ['# EURUSD Multi-Timeframe Benchmark', '']
    for tf in TIMEFRAMES:
        lines.append(f'## {tf}')
        for e in results[tf]:
            lines.append(f"- {e['model']}: avg_accuracy={e['average_accuracy']} std={e['std_accuracy']} folds={e['folds']}")
        lines.append('')
    lines.append('## Promotion Decision')
    lines.append(json.dumps(promo, indent=2))
    md.write_text('\n'.join(lines))

    print('Benchmarks complete')
    return results, promo

if __name__ == '__main__':
    run_benchmarks()
