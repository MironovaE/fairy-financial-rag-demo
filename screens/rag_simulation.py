# screens/rag_simulation.py
import streamlit as st
import os
import torch

# Отключаем GPU (на Streamlit Cloud нет CUDA)
os.environ["CUDA_VISIBLE_DEVICES"] = ""
torch.set_num_threads(1)

# === Попытка 1: sentence-transformers ===
SENTENCE_TRANSFORMERS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    pass

# === Попытка 2: TF-IDF ===
TFIDF_AVAILABLE = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    TFIDF_AVAILABLE = True
except Exception:
    pass

# === Загрузка модели эмбеддингов (с кэшированием) ===
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# === Фильтрация: эмбеддинги ===
def filter_with_embeddings(products, query):
    model = load_embedding_model()
    query_emb = model.encode(query, convert_to_tensor=True, show_progress_bar=False)
    product_texts = [f"{p['name']}. {p.get('description', '')}" for p in products]
    product_embs = model.encode(product_texts, convert_to_tensor=True, show_progress_bar=False)
    similarities = util.cos_sim(query_emb, product_embs)[0]
    top_k = min(5, len(products))
    top_indices = torch.topk(similarities, k=top_k).indices
    return [products[i] for i in top_indices]

# === Фильтрация: TF-IDF ===
def filter_with_tfidf(products, query):
    product_texts = [f"{p['name']} {p.get('description', '')}".lower() for p in products]
    query_text = query.lower()
    vectorizer = TfidfVectorizer(stop_words=None, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(product_texts + [query_text])
    query_vec = tfidf_matrix[-1]
    product_vecs = tfidf_matrix[:-1]
    similarities = cosine_similarity(query_vec, product_vecs).flatten()
    top_indices = np.argsort(similarities)[::-1][:5]
    return [products[i] for i in top_indices if similarities[i] > 0.05]

# === Фильтрация: ключевые слова ===
def filter_with_keywords(products, query):
    query_lower = query.lower()
    saving = ["накопить", "вклад", "сбережения", "мальдив", "мечта", "цель", "копить"]
    credit = ["заем", "кредит", "долг", "срочно", "занять"]
    if any(kw in query_lower for kw in saving):
        return [p for p in products if p.get("type") in ["вклад", "сберегательный счёт", "целевой счёт"]]
    elif any(kw in query_lower for kw in credit):
        return [p for p in products if p.get("type") in ["кредит", "заем"]]
    return products[:5]

# === Выбор метода ===
def get_relevant_products(products, query):
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            return filter_with_embeddings(products, query), "эмбеддинги"
        except Exception:
            pass
    if TFIDF_AVAILABLE:
        try:
            return filter_with_tfidf(products, query), "TF-IDF"
        except Exception:
            pass
    return filter_with_keywords(products, query), "ключевые слова"

# === Формирование промпта ===
def build_rag_prompt(hero, query, relevant_products):
    top_products = relevant_products[:5]
    products_text = "\n".join(
        f"- **{p['name']}**: {p.get('description', 'Описание отсутствует')}"
        for p in top_products
    )
    return f"""Ты — Сундук Мудрости, сказочный советник Княжеского банка.
Герой: {hero['name']}, возраст {hero['age']}, доход {hero['income']} золотых, гражданство: {hero['citizenship']}.
Его финансовая цель: "{query}"

Доступные релевантные продукты:
{products_text}

Сформулируй тёплый, сказочный, полезный совет в 3–5 предложениях.
Не упоминай реальные бренды, валюты или страны.
Используй образы русских сказок: жёлуди, терема, богатыри, злато, мудрость."""


# === Основной экран ===
def show():
    st.title("🧠 RAG-имитация: подготовка контекста для LLM")

    st.markdown("""
    На этом этапе мы отбираем **наиболее релевантные финансовые продукты** из уже допустимых (отфильтрованных по возрасту, доходу и гражданству).
    
    Для этого мы используем **иерархический подход**:
    - Сначала пытаемся применить **семантические эмбеддинги** (наиболее точный метод),
    - Если они недоступны — переключаемся на **TF-IDF** (статистический метод),
    - В крайнем случае — используем **ключевые слова** (гарантированная логика).
    
    Такой подход обеспечивает **максимальное качество при полной отказоустойчивости**.
    """)

    # 🔹 Таблица методов
    st.subheader("🛠 Используемые методы отбора")
    st.markdown("""
| Метод | Условие применения | Качество |
|------|-------------------|--------|
| **Эмбеддинги** | Если `sentence-transformers` импортировался и хватило памяти | Высокое |
| **TF-IDF** | Если эмбеддинги упали, но `scikit-learn` работает | Хорошее |
| **Ключевые слова** | Если всё упало (крайне редко) | Базовая логика |
""")

    hero = st.session_state["hero"]
    query = st.session_state.get("user_query", "Не указана")
    eligible_products = st.session_state["eligible_products"]

    # Отбор релевантных продуктов
    relevant_products, method = get_relevant_products(eligible_products, query)
    st.success(f"✅ Отобрано {len(relevant_products)} самых релевантных продуктов (метод: **{method}**).")

    # Показываем отобранные продукты
    with st.expander("📦 Релевантные продукты (ТОП-5)", expanded=True):
        for p in relevant_products:
            st.markdown(f"**{p['name']}** — {p.get('description', 'Описание отсутствует')}")

    # Формируем промпт
    prompt = build_rag_prompt(hero, query, relevant_products)
    st.subheader("📜 Сформированный промпт для LLM")
    st.code(prompt, language="text")
    st.info("Этот промпт будет отправлен в языковую модель для генерации финального совета.")

    # Кнопка перехода к генерации (без вызова LLM здесь!)
    if st.button("➤ Отправить в LLM"):
        st.session_state["final_prompt"] = prompt
        st.session_state["screen"] = "llm_response"
        st.rerun()