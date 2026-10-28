import streamlit as st

from utils import Key, go, restart, step_header

EXAMPLES = [
    "Хочу накопить на терем за год",
    "Нужен заём на нового коня",
    "Как отложить на старость?",
]


def show():
    hero = st.session_state[Key.HERO]

    step_header(
        "query_input",
        f"Здравствуй, {hero['name']}!",
        "Расскажи, какую финансовую цель хочешь достичь — Сундук подберёт, что предложить.",
    )

    with st.form("query"):
        query = st.text_area(
            "Вопрос",
            placeholder="Например: «Как накопить на терем на Мальдивах за два месяца?»",
            height=100,
        )
        st.caption("Ещё идеи: " + " · ".join(f"«{e}»" for e in EXAMPLES))
        submitted = st.form_submit_button("Получить совет", type="primary")

    if submitted:
        if query.strip():
            st.session_state[Key.QUERY] = query.strip()
            go("product_loader")
            st.rerun()
        else:
            st.error("Напишите вопрос.")

    st.button("Выйти", on_click=restart)
