#!/usr/bin/env python3
"""Run FeatureSelector safely on Colab with optional sampling.

Saves ranking to Drive and updates CHECKLIST.md (attempts git commit/push).

Usage:
  python run_feature_selector.py --sample-frac 0.3 --push
"""
import os
import sys
import json
import subprocess


def is_colab():
    try:
        import google.colab  # type: ignore
        return True
    except Exception:
        pass
    if os.path.exists('/content'):
        return True
    return False


def update_checklist_mark():
    path = os.path.join(os.getcwd(), 'CHECKLIST.md')
    if not os.path.exists(path):
        print('CHECKLIST.md not found, skipping update')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    if 'Auto Feature Selection' in txt and '[x]' in txt:
        print('Auto Feature Selection already marked')
        return True
    # naive replacement: find "Auto Feature Selection" line and mark it
    lines = txt.splitlines()
    for i,l in enumerate(lines):
        if 'Auto Feature Selection' in l:
            lines[i] = lines[i].replace('[ ]', '[x]') if '[ ]' in lines[i] else lines[i]
            break
    out = '\n'.join(lines)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)
    return True


def try_git_commit_push(message='docs: mark Auto Feature Selection done'):
    try:
        subprocess.check_call(['git', 'add', 'CHECKLIST.md'])
        subprocess.check_call(['git', 'commit', '-m', message])
        subprocess.check_call(['git', 'push'])
        return True
    except Exception as e:
        print('git commit/push failed:', e)
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-frac', type=float, default=0.3, help='Fraction of rows to sample to limit CPU')
    parser.add_argument('--push', action='store_true', help='Attempt git commit & push after updating CHECKLIST')
    parser.add_argument('--allow-local', action='store_true', help='Allow running outside Colab')
    args = parser.parse_args()

    if not is_colab() and not args.allow_local:
        print('Refusing to run: not detected Colab. Use --allow-local to override.')
        sys.exit(2)

    os.environ.setdefault('OMP_NUM_THREADS','2')
    os.environ.setdefault('MKL_NUM_THREADS','2')

    # run FeatureSelector logic
    try:
        from app.research.feature_selector import FeatureSelector
        from app.research.experiment_generator import Experiment
    except Exception as e:
        print('Import error:', e)
        sys.exit(3)

    exp = Experiment(market='BTCUSDT', model='xgboost', target='classification_up_down_5', feature_set='default')
    fs = FeatureSelector()

    # use internal _prepare to get df and features, then sample
    df, features, y = fs._prepare(exp, timeframe='1d')
    if df.empty:
        print('Prepared dataframe is empty; aborting')
        sys.exit(4)

    if args.sample_frac < 1.0:
        df = df.sample(frac=args.sample_frac, random_state=42).reset_index(drop=True)
        print(f'Sampled dataframe to {len(df)} rows ({args.sample_frac*100:.1f}%)')

    # write sampled temp file (not used by FeatureSelector directly)
    out_dir = '/content/drive/MyDrive/aqrs-results'
    os.makedirs(out_dir, exist_ok=True)

    # replicate ranking code here with sampled df
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

    # save results
    out_path = os.path.join(out_dir, 'feature_ranking.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'baseline': baseline, 'ranking': ranked}, f, indent=2)

    print('Saved ranking to', out_path)
    print('\nTOP FEATURES')
    for i, (name, delta) in enumerate(ranked[:20], start=1):
        print(f'{i} {name} {delta:.4f}')

    # update checklist
    updated = update_checklist_mark()
    if updated:
        print('Updated CHECKLIST.md')
        if args.push:
            ok = try_git_commit_push()
            if ok:
                print('Pushed checklist update')
            else:
                print('Push failed (check git credentials in Colab)')
    else:
        print('Checklist not updated')


if __name__ == '__main__':
    main()
