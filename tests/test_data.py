import io

import pytest

from rag.data import DataError, parse_json, validate_heroes, validate_products


def test_demo_files_are_valid(heroes, products):
    assert validate_heroes(heroes) == heroes
    assert validate_products(products) == products


@pytest.mark.parametrize("items", [[], {}, "герои", None])
def test_not_a_list_is_rejected(items):
    with pytest.raises(DataError, match="непустой массив"):
        validate_heroes(items)


def test_every_item_is_checked_not_only_the_first(heroes):
    broken = heroes + [{"card_suffix": "4321", "name": "Кощей"}]
    with pytest.raises(DataError, match=r"№12: нет полей age, citizenship, income"):
        validate_heroes(broken)


def test_wrong_types_are_reported(heroes):
    hero = dict(heroes[0], card_suffix=1111, age="двадцать")
    with pytest.raises(DataError) as e:
        validate_heroes([hero])
    assert "card_suffix" in str(e.value)
    assert "age" in str(e.value)


def test_duplicate_card_is_rejected(heroes):
    with pytest.raises(DataError, match="уже был выше"):
        validate_heroes([heroes[0], dict(heroes[1], card_suffix=heroes[0]["card_suffix"])])


def test_bad_eligibility_is_rejected(products):
    product = dict(products[0], eligibility={"min_age": "18", "citizenship_allowed": [1]})
    with pytest.raises(DataError) as e:
        validate_products([product])
    assert "min_age" in str(e.value)
    assert "citizenship_allowed" in str(e.value)


def test_long_list_of_problems_is_shortened():
    with pytest.raises(DataError, match="и ещё 5"):
        validate_products([{"id": str(i)} for i in range(10)])


def test_broken_json_gives_readable_error():
    with pytest.raises(DataError, match="Не получилось прочитать JSON"):
        parse_json(io.BytesIO(b"[{"))


def test_uploaded_file_can_be_read_twice():
    upload = io.BytesIO('[{"a": 1}]'.encode())
    assert parse_json(upload) == parse_json(upload)
