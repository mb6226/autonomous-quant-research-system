# Google Colab Setup for AQRS

This document describes how to prepare a Google Colab environment to run AQRS research workloads (walk-forward benchmarks, experiment runner, promotion engine) using Google Drive for storage.

Prereqs (on Colab)
- Select Runtime → Change runtime type → Python 3.12 (if available) and set Hardware accelerator to `None` or `GPU` depending on model needs.
- Mount Google Drive (see below).

Quick steps

1. Mount Google Drive (run in a Colab cell):

```python
from google.colab import drive
drive.mount('/content/drive')
```

2. Clone the repository into Drive (example):

```bash
%cd /content/drive/MyDrive
git clone https://github.com/your-org/autonomous-quant-research-system.git
%cd autonomous-quant-research-system
```

3. Install Python requirements (use a virtual env inside Colab session is optional):

```bash
pip install -r requirements.txt
# If some packages need system libs, install them (example):
sudo apt-get update && sudo apt-get install -y build-essential libgomp1
```

4. Set `PYTHONPATH` so the repo is importable:

```bash
export REPO_DIR=/content/drive/MyDrive/autonomous-quant-research-system
export PYTHONPATH="$REPO_DIR":$PYTHONPATH
```

5. Verify imports and parquet access:

```python
import sys
sys.path.insert(0, '/content/drive/MyDrive/autonomous-quant-research-system')
import app
import pandas as pd
pd.read_parquet('data/raw/EURUSD/1m.parquet').head()
```

Notes
- Use `/content/drive/MyDrive/<folder>` for persistent storage.
- Avoid running Dukascopy downloads from Colab; copy pre-existing parquet files to Drive first.
- For long-running runs consider Colab Pro+ or a paid VM (GCE) for guaranteed CPU/RAM.
