import streamlit as st


class Key:
    """Ключи st.session_state — в одном месте, чтобы экраны не разошлись в написании."""

    SCREEN = "screen"
    HEROES = "heroes_data"
    HERO = "hero"
    QUERY = "user_query"
    PRODUCTS = "products_data"
    ELIGIBLE = "eligible_products"
    RELEVANT = "relevant_products"
    # (хэш каталога, коллекция Chroma этой сессии или None)
    STORE = "vector_store"
    PROMPT = "final_prompt"
    ANSWER = "llm_response"
    ANSWER_IS_FALLBACK = "llm_fallback"

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
    st.session_state[Key.SCREEN] = screen


def restart():
    st.session_state.clear()


def step_header(screen, title, subtitle=None):
    step = STEPS.index(screen) + 1
    st.markdown(f'<p class="fairy-chapter-label">Глава {step} из {len(STEPS)}</p>', unsafe_allow_html=True)
    st.progress(step / len(STEPS))
    st.title(title)
    if subtitle:
        st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)

