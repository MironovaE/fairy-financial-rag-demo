import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    TFIDF_AVAILABLE = True
except ImportError:
    TFIDF_AVAILABLE = False

TOP_K = 5

# Ниже порога продукт считаем не относящимся к вопросу. У эмбеддингов сходство выше даже
# у случайных пар, поэтому и порог выше: на демо-данных бессмыслица вроде «ываыва» набирает до 0.25
EMBEDDING_THRESHOLD = 0.3
TFIDF_THRESHOLD = 0.05

METHOD_CHROMA = "векторная база Chroma"
METHOD_EMBEDDINGS = "эмбеддинги"
METHOD_TFIDF = "TF-IDF"
METHOD_KEYWORDS = "ключевые слова"

# Корни слов из вопроса → типы продуктов. Вопрос может попасть в несколько групп сразу
KEYWORD_GROUPS = [
    (
        ("накоп", "вклад", "сбереж", "отлож", "копить", "мечт", "цель", "резерв", "чёрный день", "непредвид"),
        {"deposit", "savings", "goal_savings", "emergency"},
    ),
    (("пенси", "старост"), {"pension", "deposit"}),
    (("заём", "заем", "займ", "кредит", "долг", "занять", "ипотек", "срочно", "терем"), {"loan", "mortgage"}),
    (("карт", "кэшбэк", "покупк"), {"card"}),
    (("бизнес", "лавк", "магазин", "предприним", "своё дело", "свое дело"), {"business"}),
    (("инвест", "вложи", "вложить", "приумнож", "прибыл", "доходн", "вексел"), {"investment"}),
    (("страх", "защит", "колдун", "порч", "заклят"), {"insurance"}),
    (("сейф", "хран", "ценност", "спрятать", "вор"), {"safe"}),
    (("подписк", "ежемесяч", "стрим", "амулет", "привилег"), {"subscription"}),
]


def product_text(product):
    return product.get("text", "").strip() or f"{product['name']}. {product.get('description', '')}"


def top_by_score(products, scores, threshold, top_k=TOP_K):
    order = np.argsort(scores)[::-1][:top_k]
    return [(products[i], float(scores[i])) for i in order if scores[i] >= threshold]


def search_embeddings(products, product_vectors, query_vector, threshold=EMBEDDING_THRESHOLD):
    """Векторы уже нормированы, так что скалярное произведение — это косинус."""
    scores = np.asarray(product_vectors) @ np.asarray(query_vector)
    return top_by_score(products, scores, threshold)


def search_tfidf(products, query, threshold=TFIDF_THRESHOLD):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([product_text(p).lower() for p in products] + [query.lower()])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    return top_by_score(products, scores, threshold)


def keyword_types(query):
    query = query.lower()
    return set().union(*(types for words, types in KEYWORD_GROUPS if any(w in query for w in words)))


def search_keywords(products, query):
    """Без сходства: продукты подходящих типов в порядке каталога. Ничего не узнали — первые TOP_K."""
    types = keyword_types(query)
    if not types:
        return [(p, None) for p in products[:TOP_K]]
    return [(p, None) for p in products if p.get("type") in types][:TOP_K]


def search_store(store, products, hero, query_vector, threshold=EMBEDDING_THRESHOLD):
    """
    Поиск в векторной базе: фильтр по правилам делает сама база условием where.

    Главный всё равно rag.eligibility: если база вернула то, чего нет среди products, это ошибка
    в переводе правил, такое выбрасываем и пишем в лог.
    """
    allowed = {p["id"] for p in products}
    results = store.search(query_vector, hero, threshold, TOP_K)
    extra = [p["id"] for p, _ in results if p["id"] not in allowed]
    if extra:
        logger.error("Chroma filter let through ineligible products: %s", extra)
    return [(p, score) for p, score in results if p["id"] in allowed]


def get_relevant_products(products, query, embed=None, store=None, hero=None):
    """
    Продукты, близкие к вопросу, и название сработавшего метода.

    products — уже отфильтрованные по правилам. embed(texts) → нормированные векторы; None —
    эмбеддингов нет, сразу TF-IDF. store — векторная база со всем каталогом (rag.vector_store),
    hero нужен ей для фильтра; без них поиск идёт по векторам в памяти.
    """
    if not products:
        return [], METHOD_KEYWORDS
    if embed is not None and store is not None and hero is not None:
        try:
            return search_store(store, products, hero, embed([query])[0]), METHOD_CHROMA
        except Exception:
            logger.exception("Chroma search failed, searching embeddings in memory")
    if embed is not None:
        try:
            vectors = embed([product_text(p) for p in products] + [query])
            return search_embeddings(products, vectors[:-1], vectors[-1]), METHOD_EMBEDDINGS
        except Exception:
            logger.exception("Embedding search failed, falling back to TF-IDF")
    if TFIDF_AVAILABLE:
        try:
            return search_tfidf(products, query), METHOD_TFIDF
        except Exception:
            logger.exception("TF-IDF search failed, falling back to keywords")
    return search_keywords(products, query), METHOD_KEYWORDS
