#!/bin/bash
# One-time setup on a Mac. Run from the repo folder:  bash setup/setup_mac.sh
set -e
cd "$(dirname "$0")/.."
if ! command -v python3 >/dev/null; then
  echo "Python 3 isn't installed. Get it from https://www.python.org/downloads/ and run this again."; exit 1
fi
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install -r requirements.txt -q
.venv/bin/python tools/doctor.py
