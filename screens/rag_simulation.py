import logging

import streamlit as st

from rag import embedder, vector_store
from rag.prompt import build_rag_prompt
from rag.retrieval import get_relevant_products, product_text
from utils import Key, go, step_header

logger = logging.getLogger(__name__)


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


def product_store(products, embed):
    """
    Коллекция Chroma этой сессии. Пересобирается, только если поменялся каталог;
    старая коллекция при этом удаляется. None — Chroma недоступна.
    """
    key = vector_store.catalog_key(products)
    cached = st.session_state.get(Key.STORE)
    if cached is not None and cached[0] == key:
        return cached[1]
    if cached is not None and cached[1] is not None:
        cached[1].close()

    texts = [product_text(p) for p in products]
    store = None
    with st.spinner("Складываем продукты в векторную базу…"):
        try:
            store = vector_store.build_store(products, embed(texts), texts)
        except Exception:
            logger.exception("Failed to embed the catalog for Chroma")
    st.session_state[Key.STORE] = (key, store)
    return store


def show_store(store, hero):
    with st.expander("Что лежит в векторной базе"):
        st.markdown(f"Коллекция `{store.name}`, записей: {store.count()}. Своя у каждой сессии, живёт в памяти.")
        st.markdown("Фильтр по правилам для этого героя — условие `where`:")
        st.json(vector_store.eligibility_where(hero))
        st.markdown("Первые записи — текст продукта и метаданные:")
        st.json(store.peek(3))
        st.caption(f"±{vector_store.NO_LIMIT:.0f} в метаданных — ограничения нет.")


def show():
    step_header(
        "rag_simulation",
        "Поиск и промпт",
        "Из подходящих продуктов выбираем самые близкие к вопросу и собираем промпт для модели.",
    )

    hero = st.session_state[Key.HERO]
    query = st.session_state[Key.QUERY]

    products = st.session_state[Key.PRODUCTS]
    embed = make_embed(products)
    store = product_store(products, embed) if embed is not None else None
    results, method = get_relevant_products(st.session_state[Key.ELIGIBLE], query, embed, store, hero)
    relevant = [p for p, _ in results]
    st.session_state[Key.RELEVANT] = relevant

    st.markdown(f"**Метод поиска:** {method}")
    st.caption(
        "Сначала векторная база Chroma; если её нет — те же эмбеддинги в памяти; если модель не загрузилась — "
        "TF-IDF; если и он недоступен — ключевые слова."
    )
    if store is not None:
        show_store(store, hero)

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
