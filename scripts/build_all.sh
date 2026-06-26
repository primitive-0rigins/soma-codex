#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/src"

python3 build.py book0-overview.html
python3 build.py book1-theory.html
python3 build.py book2-anatomy.html
python3 build.py book3-physiology.html
python3 build.py book4-engineering.html
python3 build.py book5-runtime.html
python3 build.py appendices.html
