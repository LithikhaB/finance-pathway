"""Point the app at a throwaway database before any app module is imported,
so running the test suite never touches (or reuses stale data from) the
real data/app.db.
"""
import os
from pathlib import Path

_TEST_DB = Path(__file__).parent / "_test.db"
_TEST_DB.unlink(missing_ok=True)
os.environ["FINANCE_PATHWAY_DB"] = str(_TEST_DB)