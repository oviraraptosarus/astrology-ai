"""Make project root importable for tests run from tests/ (script dir lands on
sys.path, not the project root). Works under plain `python tests/test_x.py`,
pytest, and unittest discovery."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
