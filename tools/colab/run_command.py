#!/usr/bin/env python3
"""Simple launcher for Colab: runs a shell command with PYTHONPATH set to repo.
Usage: python run_command.py --repo /content/repo --cmd "python -m pytest -q tests/test_feature_selector.py -q"
"""
import os
import sys
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--repo', default='/content/repo')
parser.add_argument('--cmd', required=True)
parser.add_argument('--env', nargs='*', default=[])
args = parser.parse_args()

env = os.environ.copy()
env['PYTHONPATH'] = args.repo + (':' + env.get('PYTHONPATH',''))
for e in args.env:
    if '=' in e:
        k,v = e.split('=',1)
        env[k]=v

print('Running command:', args.cmd)
print('PYTHONPATH=', env['PYTHONPATH'])
ret = subprocess.call(args.cmd, shell=True, env=env)
sys.exit(ret)
