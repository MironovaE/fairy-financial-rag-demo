import streamlit as st

from rag.eligibility import split_by_eligibility
from rag.prompt import hero_summary
from utils import Key, go, step_header


def show():
    step_header(
        "preprocessing",
        "Фильтрация по правилам",
        "До всякого поиска отсеиваем то, что герою не положено по возрасту, доходу и гражданству.",
    )

    hero = st.session_state[Key.HERO]
    products = st.session_state[Key.PRODUCTS]

    st.markdown(f"**Герой:** {hero_summary(hero)}")
    st.markdown(f"**Вопрос:** «{st.session_state[Key.QUERY]}»")

    eligible, rejected = split_by_eligibility(products, hero)
    st.session_state[Key.ELIGIBLE] = eligible

    eligible_col, rejected_col = st.columns(2)
    eligible_col.metric("Подходят", len(eligible))
    rejected_col.metric("Отсеяно", len(rejected))

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
