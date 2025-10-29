# screens/auth.py
import streamlit as st

def show():
    st.markdown("## 🏦 Сундук Мудрости")
    st.markdown("*Сказочный финансовый советник Княжеского банка*")
    st.markdown("### 🔑 Авторизация")

    # Загружаем список героев (ожидается список словарей)
    heroes = st.session_state.get("heroes_data", [])

    # Аккордеон с героями — показываем, только если есть данные и это список
    if isinstance(heroes, list) and len(heroes) > 0:
        with st.expander("📖 Доступные герои"):
            for profile in heroes:
                suffix = profile.get("card_suffix", "????")
                name = profile.get("name", "Безымянный герой")
                age = profile.get("age", "—")
                income = profile.get("income", "—")
                citizenship = profile.get("citizenship", "—")
                st.markdown(f"**{suffix}** — {name}, {age} лет, {income} золотых, {citizenship}")

    # Поле ввода последних 4 цифр
    card_suffix = st.text_input(
        "Введите последние 4 цифры вашей карты:",
        max_chars=4,
        placeholder="Например: 1111"
    )

    # Кнопка входа
    if st.button("Войти в Сундук Мудрости"):
        if len(card_suffix) == 4 and card_suffix.isdigit():
            st.session_state["card_suffix"] = card_suffix

            # Поиск героя по card_suffix в списке
            hero = None
            for h in heroes:
                if str(h.get("card_suffix")) == card_suffix:
                    hero = h
                    break

            if hero:
                st.session_state["hero"] = hero
            else:
                # Герой не найден — создаём заглушку
                st.session_state["hero"] = {
                    "name": f"Неизвестный герой ({card_suffix})",
                    "age": None,
                    "income": None,
                    "citizenship": None,
                    "card_suffix": card_suffix,
                    "traits": "Не найден среди загруженных профилей"
                }

            st.session_state["screen"] = "query_input"
            st.rerun()
        else:
            st.error("Пожалуйста, введите ровно 4 цифры.")