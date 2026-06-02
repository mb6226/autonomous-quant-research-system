#!/usr/bin/env python3
"""Colab launcher: ensures heavy jobs run only on Google Colab.

Usage:
  python colab_launcher.py --cmd "<shell command>" [--repo /content/repo] [--allow-local]

By default this script refuses to run if it doesn't detect Google Colab environment.
Set --allow-local to override (use carefully).
"""
import os
import sys
import subprocess


def is_colab():
    # Preferred detection: google.colab module
    try:
        import google.colab  # type: ignore
        return True
    except Exception:
        pass
    # Fallback heuristics
    if os.path.exists('/content') and ('COLAB_GPU' in os.environ or os.path.exists('/content/repo')):
        return True
    return False


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', required=True, help='Shell command to run')
    parser.add_argument('--repo', default='/content/repo', help='Path to cloned repo (used to set PYTHONPATH)')
    parser.add_argument('--allow-local', action='store_true', help='Allow running on local machine (unsafe)')
    args = parser.parse_args()

    if not is_colab() and not args.allow_local:
        sys.stderr.write('Refusing to run heavy command: Colab environment not detected. Use --allow-local to override.\n')
        sys.exit(2)

    env = os.environ.copy()
    current = env.get('PYTHONPATH','')
    env['PYTHONPATH'] = args.repo + (':' + current if current else '')

    print('Launching command on host:', 'google.colab' if is_colab() else 'local')
    print('Command:', args.cmd)
    rc = subprocess.call(args.cmd, shell=True, env=env)
    sys.exit(rc)
