# streamlit run app.py
from pathlib import Path

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
    layout="wide",
)

css = (Path(__file__).resolve().parent / "assets" / "theme.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

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
