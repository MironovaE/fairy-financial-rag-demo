import logging

import streamlit as st
from groq import Groq

from rag.prompt import fallback_response, hero_summary
from utils import go, restart, step_header

logger = logging.getLogger(__name__)

MODEL = "openai/gpt-oss-20b"


def groq_api_key():
    try:
        return st.secrets.get("GROQ_API_KEY")
    except FileNotFoundError:
        # локально без .streamlit/secrets.toml
        return None


def call_groq(prompt):
    """Ответ модели или None, если Groq недоступен."""
    api_key = groq_api_key()
    if not api_key:
        logger.warning("GROQ_API_KEY is not set, showing the template answer")
        return None
    try:
        response = Groq(api_key=api_key).chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            # gpt-oss сначала рассуждает, и рассуждения тоже тратят лимит токенов
            max_tokens=1024,
            extra_body={"reasoning_effort": "low"},
        )
        return response.choices[0].message.content.strip()
    except Exception:
        logger.exception("Groq request failed")
        return None


def show():
    step_header("llm_response", "Совет Сундука")

    hero = st.session_state["hero"]
    query = st.session_state["user_query"]

    st.markdown(f"**Герой:** {hero_summary(hero)}")
    st.markdown(f"**Вопрос:** «{query}»")

    if "llm_response" not in st.session_state:
        with st.spinner("Сундук думает…"):
            answer = call_groq(st.session_state["final_prompt"])
        st.session_state["llm_response"] = answer
        st.session_state["llm_fallback"] = answer is None
        if answer is None:
            st.session_state["llm_response"] = fallback_response(
                hero, query, st.session_state.get("relevant_products", [])
            )

    with st.container(border=True):
        st.markdown(st.session_state["llm_response"])
    if st.session_state["llm_fallback"]:
        st.caption("Модель сейчас недоступна, поэтому показан шаблонный ответ по самому релевантному продукту.")
    else:
        st.caption(f"Ответ сгенерирован моделью {MODEL} через Groq.")

    st.divider()
    col1, col2, _ = st.columns([1, 1, 2])
    col1.button("Назад к поиску", on_click=go, args=("rag_simulation",), use_container_width=True)
    col2.button("Начать заново", on_click=restart, use_container_width=True)
