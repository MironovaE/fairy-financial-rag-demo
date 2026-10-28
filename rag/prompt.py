# С этого возраста просим модель отдать должное мудрости героя
WISE_AGE = 60


def capitalize_first(text):
    # str.capitalize() опускает остальные буквы: «Бабуля Агафья» превратилась бы в «бабуля агафья»
    return text[:1].upper() + text[1:]


def get_address_and_verb(hero):
    """Обращение и глагол в прошедшем времени по полю 'gender' героя."""
    name = hero["name"]
    if hero.get("gender") == "женский":
        return f"дорогая {name}", "обратилась"
    return f"дорогой {name}", "обратился"


def hero_summary(hero):
    return f"{hero['name']}, {hero['age']} лет, доход {hero['income']} золотых, {hero['citizenship']}"


def build_rag_prompt(hero, query, products):
    products_text = "\n".join(f"- {p['name']}: {p.get('description', '')}" for p in products)
    address, verb = get_address_and_verb(hero)

    hero_lines = [
        f"Герой: {hero['name']}, возраст {hero['age']}, доход {hero['income']} золотых, "
        f"гражданство: {hero['citizenship']}."
    ]
    traits = (hero.get("traits") or "").strip().rstrip(".")
    if traits:
        hero_lines.append(f"О герое: {traits}.")

    rules = [
        "Дай тёплый и полезный совет в 3–5 предложениях, опираясь только на эти продукты.",
        "Обращайся к герою лично, в духе русских сказок: злато, терема, богатыри.",
        "Не упоминай реальные бренды, валюты и страны: никаких рублей и долларов, деньги — только «золотые».",
    ]
    if traits:
        rules.append("Можешь обыграть характер героя, но не придумывай продуктов сверх списка.")
    if hero["age"] > WISE_AGE:
        rules.append("Герой в почтенных летах — отдай должное его мудрости и опыту.")

    hero_text = "\n".join(hero_lines)
    rules_text = "\n".join(rules)
    return f"""Ты — Сундук Мудрости, сказочный советник Княжеского банка.

{capitalize_first(address)} {verb} с финансовой целью: «{query}».
{hero_text}

Подходящие продукты банка:
{products_text}

{rules_text}"""


def fallback_response(hero, query, products):
    """Шаблонный ответ, когда модель недоступна: советуем самый релевантный продукт."""
    address, verb = get_address_and_verb(hero)
    text = f"{capitalize_first(address)}, ты {verb} с вопросом: «{query}». "
    if products:
        best = products[0]
        description = best.get("description", "").rstrip(".")
        text += f"Присмотрись: {best['name']} — {description[:1].lower()}{description[1:]}."
    else:
        text += "Подходящих продуктов пока нет — попробуй сформулировать цель иначе."
    return text
