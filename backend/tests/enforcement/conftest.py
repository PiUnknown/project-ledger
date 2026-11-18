import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
repository_root = str(REPOSITORY_ROOT)
if repository_root not in sys.path:
    sys.path.insert(0, repository_root)
