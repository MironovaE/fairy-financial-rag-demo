def rejection_reason(product, hero):
    """Почему продукт не подходит герою; None — если подходит."""
    rules = product.get("eligibility") or {}
    age, income = hero.get("age"), hero.get("income")

    if rules.get("min_age") is not None and age < rules["min_age"]:
        return f"возраст от {rules['min_age']}"
    if rules.get("max_age") is not None and age > rules["max_age"]:
        return f"возраст до {rules['max_age']}"
    if rules.get("min_income") is not None and income < rules["min_income"]:
        return f"доход от {rules['min_income']}"

    allowed = rules.get("citizenship_allowed")
    if allowed:
        if isinstance(allowed, str):
            allowed = [allowed]
        if hero.get("citizenship") not in allowed:
            return "другое гражданство"
    return None


def split_by_eligibility(products, hero):
    """Подходящие продукты и отсеянные — парами (продукт, причина)."""
    eligible, rejected = [], []
    for product in products:
        reason = rejection_reason(product, hero)
        if reason is None:
            eligible.append(product)
        else:
            rejected.append((product, reason))
    return eligible, rejected
