import streamlit as st

from utils import go, step_header


def show():
    step_header("auth", "Вход в банк", "Герой входит по последним четырём цифрам карты.")

    heroes = st.session_state.get("heroes_data", [])

    with st.expander("Кто есть в списке", expanded=True):
        st.dataframe(
            [
                {
                    "Карта": h.get("card_suffix"),
                    "Имя": h.get("name"),
                    "Возраст": h.get("age"),
                    "Доход": h.get("income"),
                    "Гражданство": h.get("citizenship"),
                }
                for h in heroes
            ],
            hide_index=True,
            use_container_width=True,
        )

    with st.form("auth"):
        card_suffix = st.text_input("Последние 4 цифры карты", max_chars=4, placeholder="1111")
        submitted = st.form_submit_button("Войти", type="primary")

    if submitted:
        hero = next((h for h in heroes if str(h.get("card_suffix")) == card_suffix), None)
        if not (len(card_suffix) == 4 and card_suffix.isdigit()):
            st.error("Нужно ровно 4 цифры.")
        elif hero is None:
            st.error("Героя с такой картой нет — выберите из списка выше.")
        else:
            st.session_state["hero"] = hero
            go("query_input")
            st.rerun()
