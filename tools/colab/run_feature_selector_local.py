#!/usr/bin/env python3
"""Run FeatureSelector locally with sampling and write artifact to repository.

Usage:
  python run_feature_selector_local.py --sample-frac 0.3
"""
import os
import sys
import json


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-frac', type=float, default=0.3)
    args = parser.parse_args()

    os.environ.setdefault('OMP_NUM_THREADS','1')
    os.environ.setdefault('MKL_NUM_THREADS','1')

    try:
        from app.research.feature_selector import FeatureSelector
        from app.research.experiment_generator import Experiment
    except Exception as e:
        print('Import error:', e)
        sys.exit(3)

    exp = Experiment(market='BTCUSDT', model='xgboost', target='classification_up_down_5', feature_set='default')
    fs = FeatureSelector()

    df, features, y = fs._prepare(exp, timeframe='1d')
    if df.empty:
        print('Prepared dataframe is empty; aborting')
        sys.exit(4)

    if args.sample_frac < 1.0:
        df = df.sample(frac=args.sample_frac, random_state=42).reset_index(drop=True)
        print(f'Sampled dataframe to {len(df)} rows ({args.sample_frac*100:.1f}%)')

    split = int(len(df) * 0.8)
    X = df[features]
    y = df['target']

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]
    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    model_impl = fs.runner._get_model_impl(exp.model)
    trained = model_impl.train(X_train, y_train)
    pred = trained.predict(X_test)
    baseline = fs.runner.metrics.classification_metrics(y_test, pred)['accuracy']

    deltas = []
    for f in features:
        subset = [c for c in features if c != f]
        if len(subset) == 0:
            new_acc = 0.0
        else:
            Xs = df[subset]
            Xs_train = Xs.iloc[:split]
            Xs_test = Xs.iloc[split:]
            trained2 = model_impl.train(Xs_train, y_train)
            pred2 = trained2.predict(Xs_test)
            new_acc = fs.runner.metrics.classification_metrics(y_test, pred2)['accuracy']
        delta = baseline - new_acc
        deltas.append((f, delta))

    ranked = sorted(deltas, key=lambda x: x[1], reverse=True)

    out_dir = os.path.join(os.getcwd(), 'artifacts')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'feature_ranking.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'baseline': baseline, 'ranking': ranked}, f, indent=2)

    print('Saved ranking to', out_path)
    print('\nBASELINE ACCURACY')
    print(f'{baseline:.6f}')
    print('\nTOP FEATURES')
    for i, (name, delta) in enumerate(ranked[:20], start=1):
        print(f'{i} {name} {delta:.6f}')


if __name__ == '__main__':
    main()
