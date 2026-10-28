from rag.eligibility import rejection_reason, split_by_eligibility

HERO = {"age": 30, "income": 50000, "citizenship": "Великое Княжество"}


def product(**rules):
    return {"id": "p", "name": "Продукт", "eligibility": rules}


def test_no_rules_means_eligible():
    assert rejection_reason(product(), HERO) is None
    assert rejection_reason({"id": "p", "name": "Без правил"}, HERO) is None


def test_age_bounds():
    assert rejection_reason(product(min_age=31), HERO) == "возраст от 31"
    assert rejection_reason(product(max_age=25), HERO) == "возраст до 25"
    assert rejection_reason(product(min_age=30, max_age=30), HERO) is None


def test_income():
    assert rejection_reason(product(min_income=60000), HERO) == "доход от 60000"
    assert rejection_reason(product(min_income=50000), HERO) is None


def test_citizenship_as_list_or_string():
    assert rejection_reason(product(citizenship_allowed=["Лесное Ханство"]), HERO) == "другое гражданство"
    assert rejection_reason(product(citizenship_allowed="Великое Княжество"), HERO) is None
    assert rejection_reason(product(citizenship_allowed=None), HERO) is None


def test_young_horse_gets_no_pension(products, hero_by_name):
    eligible, rejected = split_by_eligibility(products, hero_by_name["Конь Юлий"])
    eligible_ids = {p["id"] for p in eligible}
    assert "pension_acorn" not in eligible_ids
    assert "young_streamer_savings" in eligible_ids
    assert len(eligible) + len(rejected) == len(products)


def test_foreign_hero_gets_only_allowed_products(products, hero_by_name):
    eligible, _ = split_by_eligibility(products, hero_by_name["Соловей-разбойник"])
    assert eligible
    for p in eligible:
        assert "Лесное Ханство" in p["eligibility"]["citizenship_allowed"]
