from pathlib import Path

import pytest

from rag.data import parse_json

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def heroes():
    return parse_json(str(ROOT / "data" / "heroes.json"))


@pytest.fixture
def products():
    return parse_json(str(ROOT / "data" / "products.json"))


@pytest.fixture
def hero_by_name(heroes):
    return {h["name"]: h for h in heroes}
