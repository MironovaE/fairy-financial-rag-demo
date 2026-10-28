from rag.prompt import build_rag_prompt, capitalize_first, fallback_response, get_address_and_verb

PRODUCTS = [
    {"name": "Вклад «Золотой Жёлудь»", "description": "Надёжный вклад без риска."},
    {"name": "Резервная Котомка", "description": "Счёт для непредвиденных расходов."},
]


def test_capitalize_first_keeps_the_rest():
    assert capitalize_first("бабуля Агафья") == "Бабуля Агафья"
    assert capitalize_first("") == ""


def test_address_by_gender(hero_by_name):
    assert get_address_and_verb(hero_by_name["Любава"]) == ("дорогая Любава", "обратилась")
    assert get_address_and_verb(hero_by_name["Илья Муромец"]) == ("дорогой Илья Муромец", "обратился")


def test_prompt_contains_hero_query_and_products(hero_by_name):
    prompt = build_rag_prompt(hero_by_name["Илья Муромец"], "Хочу накопить на терем", PRODUCTS)
    assert "Дорогой Илья Муромец обратился" in prompt
    assert "«Хочу накопить на терем»" in prompt
    assert "- Вклад «Золотой Жёлудь»: Надёжный вклад без риска." in prompt
    assert "О герое: Силач, защищает рубежи, любит кашу." in prompt


def test_wisdom_line_only_for_elders(hero_by_name):
    young = build_rag_prompt(hero_by_name["Алёша Попович"], "вопрос", PRODUCTS)
    elder = build_rag_prompt(hero_by_name["Тихон"], "вопрос", PRODUCTS)
    assert "мудрости" not in young
    assert "мудрости" in elder


def test_prompt_without_traits(hero_by_name):
    hero = dict(hero_by_name["Любава"])
    del hero["traits"]
    prompt = build_rag_prompt(hero, "вопрос", PRODUCTS)
    assert "О герое" not in prompt
    assert "характер" not in prompt


def test_fallback_recommends_first_product(hero_by_name):
    text = fallback_response(hero_by_name["Любава"], "Куда отложить?", PRODUCTS)
    assert text.startswith("Дорогая Любава, ты обратилась с вопросом: «Куда отложить?».")
    assert "Вклад «Золотой Жёлудь» — надёжный вклад без риска." in text


def test_fallback_without_products(hero_by_name):
    text = fallback_response(hero_by_name["Тихон"], "вопрос", [])
    assert "Подходящих продуктов пока нет" in text
