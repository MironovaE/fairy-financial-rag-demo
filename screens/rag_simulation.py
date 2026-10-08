import os

import numpy as np
import streamlit as st
import torch

from utils import capitalize_first, get_address_and_verb, go, step_header

# На Streamlit Cloud нет GPU, а лишние потоки только съедают память
os.environ["CUDA_VISIBLE_DEVICES"] = ""
torch.set_num_threads(1)

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    TFIDF_AVAILABLE = True
except Exception:
    TFIDF_AVAILABLE = False

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5

SAVING_KEYWORDS = ["накоп", "вклад", "сбереж", "отлож", "копить", "мечт", "цель", "пенси", "старост"]
CREDIT_KEYWORDS = ["заём", "заем", "займ", "кредит", "долг", "занять", "ипотек", "срочно"]
SAVING_TYPES = {"deposit", "savings", "goal_savings", "emergency", "pension"}
CREDIT_TYPES = {"loan", "mortgage", "card", "business"}


@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


def product_text(p):
    return p.get("text", "").strip() or f"{p['name']}. {p.get('description', '')}"


def search_embeddings(products, query):
    model = load_embedding_model()
    query_emb = model.encode(query, convert_to_tensor=True, show_progress_bar=False)
    product_embs = model.encode([product_text(p) for p in products], convert_to_tensor=True, show_progress_bar=False)
    scores = util.cos_sim(query_emb, product_embs)[0]
    top = torch.topk(scores, k=min(TOP_K, len(products)))
    return [(products[i], float(s)) for s, i in zip(top.values, top.indices)]


def search_tfidf(products, query):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([product_text(p).lower() for p in products] + [query.lower()])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    top = np.argsort(scores)[::-1][:TOP_K]
    return [(products[i], float(scores[i])) for i in top if scores[i] > 0.05]


def search_keywords(products, query):
    query = query.lower()
    if any(kw in query for kw in SAVING_KEYWORDS):
        types = SAVING_TYPES
    elif any(kw in query for kw in CREDIT_KEYWORDS):
        types = CREDIT_TYPES
    else:
        return [(p, None) for p in products[:TOP_K]]
    return [(p, None) for p in products if p.get("type") in types][:TOP_K]


def get_relevant_products(products, query):
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            return search_embeddings(products, query), "эмбеддинги"
        except Exception:
            pass
    if TFIDF_AVAILABLE:
        try:
            return search_tfidf(products, query), "TF-IDF"
        except Exception:
            pass
    return search_keywords(products, query), "ключевые слова"


def build_rag_prompt(hero, query, products):
    products_text = "\n".join(f"- {p['name']}: {p.get('description', '')}" for p in products)
    address, verb = get_address_and_verb(hero)

    return f"""Ты — Сундук Мудрости, сказочный советник Княжеского банка.

{capitalize_first(address)} {verb} с финансовой целью: «{query}».
Герой: {hero['name']}, возраст {hero['age']}, доход {hero['income']} золотых, гражданство: {hero['citizenship']}.

Подходящие продукты банка:
{products_text}

Дай тёплый и полезный совет в 3–5 предложениях, опираясь только на эти продукты.
Обращайся к герою лично, в духе русских сказок: злато, терема, богатыри.
Не упоминай реальные бренды, валюты и страны: никаких рублей и долларов, деньги — только «золотые».
Если герою больше 60 лет, отдай должное его мудрости и опыту."""


def show():
    step_header(
        "rag_simulation",
        "Поиск и промпт",
        "Из подходящих продуктов выбираем самые близкие к вопросу и собираем промпт для модели.",
    )

    hero = st.session_state["hero"]
    query = st.session_state["user_query"]

    results, method = get_relevant_products(st.session_state["eligible_products"], query)
    relevant = [p for p, _ in results]
    st.session_state["relevant_products"] = relevant

    st.markdown(f"**Метод поиска:** {method}")
    st.caption(
        "Сначала пробуем эмбеддинги; если модель не загрузилась — TF-IDF; если и он недоступен — ключевые слова."
    )

    st.subheader(f"Найдено: {len(relevant)}")
    for p, score in results:
        score_text = f" <span class='muted'>· сходство {score:.2f}</span>" if score is not None else ""
        st.markdown(f"**{p['name']}**{score_text}<br>{p.get('description', '')}", unsafe_allow_html=True)

    prompt = build_rag_prompt(hero, query, relevant)
    with st.expander("Промпт для модели"):
        st.code(prompt, language="text")

    def send():
        st.session_state["final_prompt"] = prompt
        st.session_state.pop("llm_response", None)
        go("llm_response")

    st.button("Спросить Сундук", type="primary", on_click=send, disabled=not relevant)
