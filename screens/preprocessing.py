import streamlit as st

from utils import go, hero_summary, step_header


def rejection_reason(product, hero):
    """Почему продукт не подходит герою; None — если подходит."""
    rules = product.get("eligibility", {})
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


def show():
    step_header(
        "preprocessing",
        "Фильтрация по правилам",
        "До всякого поиска отсеиваем то, что герою не положено по возрасту, доходу и гражданству.",
    )

    hero = st.session_state["hero"]
    products = st.session_state["products_data"]

    st.markdown(f"**Герой:** {hero_summary(hero)}")
    st.markdown(f"**Вопрос:** «{st.session_state['user_query']}»")

    eligible, rejected = [], []
    for p in products:
        reason = rejection_reason(p, hero)
        if reason is None:
            eligible.append(p)
        else:
            rejected.append((p, reason))
    st.session_state["eligible_products"] = eligible

    a, b = st.columns(2)
    a.metric("Подходят", len(eligible))
    b.metric("Отсеяно", len(rejected))

    with st.expander(f"Подходят ({len(eligible)})"):
        for p in eligible:
            st.markdown(f"- {p['name']}")
    if rejected:
        with st.expander(f"Отсеяно ({len(rejected)})"):
            for p, reason in rejected:
                st.markdown(f"- {p['name']} — <span class='muted'>{reason}</span>", unsafe_allow_html=True)

    if eligible:
        st.button("Дальше — поиск", type="primary", on_click=go, args=("rag_simulation",))
    else:
        st.warning("Ни один продукт не подходит этому герою — искать не из чего.")
