# screens/preprocessing.py
import streamlit as st

def filter_products_by_profile(products, hero):
    """Фильтрация продуктов по возрасту, доходу и гражданству героя.
    Поддерживает только формат с eligibility.
    """
    filtered = []
    for p in products:
        eligibility = p.get("eligibility", {})
        min_age = eligibility.get("min_age")
        max_age = eligibility.get("max_age")
        min_income = eligibility.get("min_income")
        citizenship_allowed = eligibility.get("citizenship_allowed")  # ← важно: citizenship_allowed

        # Возраст
        if min_age is not None and hero.get("age") is not None and hero["age"] < min_age:
            continue
        if max_age is not None and hero.get("age") is not None and hero["age"] > max_age:
            continue
        # Доход
        if min_income is not None and hero.get("income") is not None and hero["income"] < min_income:
            continue
        # Гражданство
        if citizenship_allowed:
            allowed = citizenship_allowed
            if isinstance(allowed, str):
                allowed = [allowed]
            if hero.get("citizenship") not in allowed:
                continue

        filtered.append(p)
    return filtered

def show():
    st.title("⚙️ Препроцессинг: отбор подходящих продуктов")

    st.markdown("""
    Подготовка списка финансовых продуктов, которые:
    - **Физически доступны герою** по его профилю (возраст, доход, гражданство),
    - **Будут использоваться дальше** в RAG-имитации для формирования промпта и генерации совета.
    """)

    hero = st.session_state["hero"]
    query = st.session_state.get("user_query", "Не указана")
    products = st.session_state["products_data"]

    # 🔹 Вывод полного профиля героя
    st.subheader("👤 Профиль героя")
    hero_info = {
        "Имя": hero.get("name", "—"),
        "Возраст": hero.get("age", "не указан") if hero.get("age") is not None else "не указан",
        "Доход": f"{hero.get('income', 'не указан')} золотых" if hero.get("income") is not None else "не указан",
        "Гражданство": hero.get("citizenship", "не указано"),
        "Номер карты (последние 4 цифры)": hero.get("card_suffix", "—"),  # ← исправлено
        "Социальный удел": hero.get("traits", "—")
    }
    for key, value in hero_info.items():
        st.markdown(f"**{key}:** {value}")

    st.markdown(f"**🎯 Запрос героя:** _«{query}»_")
    st.markdown(f"**📦 Всего продуктов в базе:** {len(products)}")

    # Выполняем фильтрацию
    eligible = filter_products_by_profile(products, hero)
    st.session_state["eligible_products"] = eligible

    st.success(f"✅ Отобрано {len(eligible)} продуктов, подходящих по возрасту, доходу и гражданству.")

    # Показываем список (кратко)
    with st.expander("📋 Список отобранных продуктов", expanded=False):
        for p in eligible:
            st.markdown(f"- **{p['name']}**")

    st.divider()
    if st.button("➡️ Перейти к RAG-имитации"):
        st.session_state["screen"] = "rag_simulation"
        st.rerun()