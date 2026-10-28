import numpy as np
import pytest

from rag import retrieval
from rag.retrieval import (
    EMBEDDING_THRESHOLD,
    KEYWORD_GROUPS,
    METHOD_EMBEDDINGS,
    METHOD_KEYWORDS,
    METHOD_TFIDF,
    TOP_K,
    get_relevant_products,
    keyword_types,
    product_text,
    search_embeddings,
    search_keywords,
    search_tfidf,
)


def test_product_text_falls_back_to_name_and_description():
    assert product_text({"name": "Вклад", "description": "Надёжный", "text": "  "}) == "Вклад. Надёжный"
    assert product_text({"name": "Вклад", "text": "Полный текст"}) == "Полный текст"


def test_embeddings_sorted_and_cut_by_threshold():
    products = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.6]])
    results = search_embeddings(products, vectors, np.array([1.0, 0.0]))
    assert [p["id"] for p, _ in results] == ["a", "c"]
    assert all(score >= EMBEDDING_THRESHOLD for _, score in results)


def test_tfidf_finds_loan(products):
    results = search_tfidf(products, "нужен заём на коня")
    assert results
    assert results[0][0]["type"] == "loan"
    assert len(results) <= TOP_K


def test_tfidf_returns_nothing_for_unrelated_query(products):
    assert search_tfidf(products, "qwerty zxcv") == []


def test_keyword_groups_cover_every_demo_type(products):
    covered = set().union(*(types for _, types in KEYWORD_GROUPS))
    assert {p["type"] for p in products} <= covered


@pytest.mark.parametrize(
    "query, expected",
    [
        ("Хочу накопить на свадьбу", "deposit"),
        ("Нужен кредит", "loan"),
        ("Куда инвестировать золото?", "investment"),
        ("Хочу застраховать артефакты", "insurance"),
        ("Где хранить ценности?", "safe"),
        ("Есть ли подписка для стримера?", "subscription"),
        ("Что отложить на старость?", "pension"),
    ],
)
def test_keyword_types(query, expected):
    assert expected in keyword_types(query)


def test_keywords_without_match_return_first_products(products):
    results = search_keywords(products, "ываыва")
    assert [p for p, _ in results] == products[:TOP_K]
    assert all(score is None for _, score in results)


def test_embeddings_used_when_available(products):
    def fake_embed(texts):
        # вопрос похож только на первый продукт
        vectors = np.zeros((len(texts), 2))
        vectors[:, 1] = 1.0
        vectors[0] = vectors[-1] = [1.0, 0.0]
        return vectors

    results, method = get_relevant_products(products, "что угодно", fake_embed)
    assert method == METHOD_EMBEDDINGS
    assert [p["id"] for p, _ in results] == [products[0]["id"]]


def test_falls_back_to_tfidf_when_embeddings_fail(products):
    def broken_embed(texts):
        raise RuntimeError("модель не загрузилась")

    _, method = get_relevant_products(products, "нужен заём", broken_embed)
    assert method == METHOD_TFIDF


def test_falls_back_to_keywords_without_sklearn(products, monkeypatch):
    monkeypatch.setattr(retrieval, "TFIDF_AVAILABLE", False)
    results, method = get_relevant_products(products, "нужен кредит")
    assert method == METHOD_KEYWORDS
    assert {p["type"] for p, _ in results} <= {"loan", "mortgage"}


def test_empty_catalog():
    assert get_relevant_products([], "вопрос") == ([], METHOD_KEYWORDS)
