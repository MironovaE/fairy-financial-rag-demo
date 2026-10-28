# streamlit run app.py
import streamlit as st

from screens import (
    auth,
    intro,
    llm_response,
    preprocessing,
    product_loader,
    profile_loader,
    query_input,
    rag_simulation,
)
from utils import Key

st.set_page_config(
    page_title="Сундук Мудрости",
    page_icon="🗝️",
    layout="centered",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2.5rem; }
    .subtitle { color: #6f6556; font-size: 1.05rem; margin-top: -0.5rem; }
    .muted { color: #6f6556; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

SCREENS = {
    "intro": intro.show,
    "profile_loader": profile_loader.show,
    "auth": auth.show,
    "query_input": query_input.show,
    "product_loader": product_loader.show,
    "preprocessing": preprocessing.show,
    "rag_simulation": rag_simulation.show,
    "llm_response": llm_response.show,
}

screen = st.session_state.setdefault(Key.SCREEN, "intro")
SCREENS.get(screen, intro.show)()
