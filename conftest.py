"""
pytest conftest.py — GlycoTwin test configuration.

Adds the project root to sys.path so tests can import src.* and app.*
without needing pip install.
"""
import sys
from pathlib import Path

# Always add project root first
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
