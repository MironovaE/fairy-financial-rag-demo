import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.data import parse_json  # noqa: E402


@pytest.fixture
def heroes():
    return parse_json(str(ROOT / "data" / "heroes.json"))


@pytest.fixture
def products():
    return parse_json(str(ROOT / "data" / "products.json"))


@pytest.fixture
def hero_by_name(heroes):
    return {h["name"]: h for h in heroes}
