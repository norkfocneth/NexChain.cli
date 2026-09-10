"""
NexSen CLI Root Launcher
Allows running NexSen directly from the project root or globally via PATH.
"""

import os
import sys
from pathlib import Path

# Add sentinel package to Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from sentinel.cli.main import run_cli

if __name__ == "__main__":
    run_cli()
