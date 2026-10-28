import streamlit as st

from rag import embedder
from rag.prompt import build_rag_prompt
from rag.retrieval import get_relevant_products, product_text
from utils import Key, go, step_header


@st.cache_resource(show_spinner="Загружаем модель эмбеддингов…")
def load_embedding_model():
    return embedder.load_model()


@st.cache_data(show_spinner="Считаем эмбеддинги продуктов…")
def catalog_vectors(texts):
    """Векторы всего каталога: считаются один раз на набор продуктов, а не на каждый вопрос."""
    model = load_embedding_model()
    return dict(zip(texts, embedder.encode(model, texts)))


def make_embed(products):
    """Функция для поиска: продукты берёт из кэша, досчитывает только вопрос. None — модели нет."""
    model = load_embedding_model()
    if model is None:
        return None
    catalog = tuple(product_text(p) for p in products)

    def embed(texts):
        cached = catalog_vectors(catalog)
        missing = [t for t in texts if t not in cached]
        fresh = dict(zip(missing, embedder.encode(model, missing))) if missing else {}
        return [cached[t] if t in cached else fresh[t] for t in texts]

    return embed


def show():
    step_header(
        "rag_simulation",
        "Поиск и промпт",
        "Из подходящих продуктов выбираем самые близкие к вопросу и собираем промпт для модели.",
    )

    hero = st.session_state[Key.HERO]
    query = st.session_state[Key.QUERY]

    embed = make_embed(st.session_state[Key.PRODUCTS])
    results, method = get_relevant_products(st.session_state[Key.ELIGIBLE], query, embed)
    relevant = [p for p, _ in results]
    st.session_state[Key.RELEVANT] = relevant

    st.markdown(f"**Метод поиска:** {method}")
    st.caption(
        "Сначала пробуем эмбеддинги; если модель не загрузилась — TF-IDF; если и он недоступен — ключевые слова."
    )

    st.subheader(f"Найдено: {len(relevant)}")
    if not relevant:
        st.info("Ни один продукт не похож на вопрос. Попробуйте сформулировать цель иначе.")
    for p, score in results:
        score_text = f" <span class='muted'>· сходство {score:.2f}</span>" if score is not None else ""
        st.markdown(f"**{p['name']}**{score_text}<br>{p.get('description', '')}", unsafe_allow_html=True)

    prompt = build_rag_prompt(hero, query, relevant)
    with st.expander("Промпт для модели"):
        st.code(prompt, language="text")

    def send():
        st.session_state[Key.PROMPT] = prompt
        st.session_state.pop(Key.ANSWER, None)
        go("llm_response")

    st.button("Спросить Сундук", type="primary", on_click=send, disabled=not relevant)
