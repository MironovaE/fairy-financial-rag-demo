import streamlit as st

from rag.data import DataError, parse_json


def _load(state_key, source, validate):
    try:
        st.session_state[state_key] = validate(parse_json(source))
    except DataError as e:
        st.session_state.pop(state_key, None)
        st.error(str(e))


def show(state_key, demo_path, validate, demo_label):
    """Кнопка демо-набора и загрузка своего JSON; общий кусок для героев и продуктов."""
    if st.button(demo_label):
        _load(state_key, demo_path, validate)

    uploaded_file = st.file_uploader("Или загрузите свой файл", type="json")
    if uploaded_file:
        _load(state_key, uploaded_file, validate)

    return st.session_state.get(state_key)
