import streamlit as st

STEPS = [
    "profile_loader",
    "auth",
    "query_input",
    "product_loader",
    "preprocessing",
    "rag_simulation",
    "llm_response",
]


def go(screen):
    st.session_state["screen"] = screen


def restart():
    st.session_state.clear()


def step_header(screen, title, subtitle=None):
    step = STEPS.index(screen) + 1
    st.caption(f"Шаг {step} из {len(STEPS)}")
    st.progress(step / len(STEPS))
    st.title(title)
    if subtitle:
        st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)

