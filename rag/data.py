import json

MAX_PROBLEMS_SHOWN = 5

HERO_FIELDS = {"card_suffix", "name", "age", "income", "citizenship"}
PRODUCT_FIELDS = {"id", "name", "description", "text", "eligibility"}


class DataError(ValueError):
    """Файл не подходит; в тексте — что именно не так."""


def _is_number(value):
    # bool — тоже int, но возраст True нам не нужен
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_text(value):
    return isinstance(value, str) and value.strip() != ""


def _hero_problems(hero):
    card = hero["card_suffix"]
    if not (isinstance(card, str) and len(card) == 4 and card.isdigit()):
        yield "card_suffix — ровно 4 цифры строкой"
    for field in ("name", "citizenship"):
        if not _is_text(hero[field]):
            yield f"{field} — непустая строка"
    for field in ("age", "income"):
        if not _is_number(hero[field]) or hero[field] < 0:
            yield f"{field} — неотрицательное число"
    for field in ("gender", "traits"):
        if hero.get(field) is not None and not isinstance(hero[field], str):
            yield f"{field} — строка"


def _product_problems(product):
    for field in ("id", "name", "description"):
        if not _is_text(product[field]):
            yield f"{field} — непустая строка"
    if not isinstance(product["text"], str):
        yield "text — строка"
    if product.get("type") is not None and not isinstance(product["type"], str):
        yield "type — строка"

    rules = product["eligibility"]
    if not isinstance(rules, dict):
        yield "eligibility — объект"
        return
    for field in ("min_age", "max_age", "min_income"):
        if rules.get(field) is not None and not _is_number(rules[field]):
            yield f"eligibility.{field} — число или null"
    allowed = rules.get("citizenship_allowed")
    if allowed is not None and not (
        isinstance(allowed, str) or (isinstance(allowed, list) and all(isinstance(c, str) for c in allowed))
    ):
        yield "eligibility.citizenship_allowed — строка, список строк или null"


def _validate(items, noun, required, item_problems, unique_field):
    if not isinstance(items, list) or not items:
        raise DataError(f"В файле должен быть непустой массив {noun}.")

    problems, seen = [], set()
    for number, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            problems.append(f"№{number}: не объект")
            continue
        missing = required - item.keys()
        if missing:
            problems.append(f"№{number}: нет полей {', '.join(sorted(missing))}")
            continue
        problems += [f"№{number}: {p}" for p in item_problems(item)]
        key = item[unique_field]
        if key in seen:
            problems.append(f"№{number}: {unique_field} «{key}» уже был выше")
        seen.add(key)

    if problems:
        shown = problems[:MAX_PROBLEMS_SHOWN]
        if len(problems) > len(shown):
            shown.append(f"и ещё {len(problems) - len(shown)}")
        raise DataError("Файл не принят: " + "; ".join(shown) + ".")
    return items


def validate_heroes(items):
    return _validate(items, "героев", HERO_FIELDS, _hero_problems, "card_suffix")


def validate_products(items):
    return _validate(items, "продуктов", PRODUCT_FIELDS, _product_problems, "id")


def parse_json(source):
    """source — путь или открытый файл (в том числе загруженный через Streamlit)."""
    try:
        if isinstance(source, str):
            with open(source, encoding="utf-8") as f:
                return json.load(f)
        # Streamlit отдаёт файл как BytesIO; на повторном проходе читаем с начала
        source.seek(0)
        return json.load(source)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise DataError(f"Не получилось прочитать JSON: {e}") from e
