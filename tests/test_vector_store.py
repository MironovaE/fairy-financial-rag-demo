import sys

import numpy as np
import pytest

from rag import vector_store
from rag.eligibility import split_by_eligibility
from rag.retrieval import (
    EMBEDDING_THRESHOLD,
    METHOD_CHROMA,
    METHOD_EMBEDDINGS,
    TOP_K,
    get_relevant_products,
    product_text,
    search_embeddings,
)
from rag.vector_store import build_store, catalog_key

pytest.importorskip("chromadb")

HERO = {"name": "Герой", "age": 30, "income": 50000, "citizenship": "Великое Княжество"}


def random_vectors(count, seed=0, dim=16):
    vectors = np.random.default_rng(seed).normal(size=(count, dim))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def make_store(products, vectors=None):
    if vectors is None:
        vectors = random_vectors(len(products))
    store = build_store(products, vectors, [product_text(p) for p in products])
    assert store is not None
    return store


def product(id, **rules):
    return {"id": id, "name": id, "description": "", "text": id, "eligibility": rules}


def test_store_holds_whole_catalog_with_metadata(products):
    store = make_store(products)
    assert store.count() == len(products)
    record = store.peek(1)[0]
    assert record["document"] == product_text(products[0])
    assert record["metadata"]["name"] == products[0]["name"]


def test_search_sorted_and_cut_by_threshold():
    products = [product("a"), product("b"), product("c")]
    store = make_store(products, np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.6]]))
    results = store.search(np.array([1.0, 0.0]), HERO, EMBEDDING_THRESHOLD, TOP_K)
    assert [p["id"] for p, _ in results] == ["a", "c"]
    # расстояние Chroma переведено обратно в косинус
    assert results[0][1] == pytest.approx(1.0)
    assert results[1][1] == pytest.approx(0.8)


def test_chroma_and_memory_search_agree(products, hero_by_name):
    vectors = random_vectors(len(products))
    store = make_store(products, vectors)
    hero = hero_by_name["Илья Муромец"]
    eligible, _ = split_by_eligibility(products, hero)
    index = [products.index(p) for p in eligible]
    query = random_vectors(1, seed=1)[0]

    in_memory = search_embeddings(eligible, vectors[index], query, threshold=-1)
    in_chroma = store.search(query, hero, -1, TOP_K)
    assert [p["id"] for p, _ in in_chroma] == [p["id"] for p, _ in in_memory]
    assert [s for _, s in in_chroma] == pytest.approx([s for _, s in in_memory], abs=1e-5)


def test_chroma_filter_matches_pure_filter_for_every_demo_hero(products, heroes):
    store = make_store(products)
    for hero in heroes:
        eligible, _ = split_by_eligibility(products, hero)
        assert store.eligible_ids(hero) == {p["id"] for p in eligible}, hero["name"]


@pytest.mark.parametrize(
    "rules",
    [
        {},
        {"min_age": 30},
        {"min_age": 31},
        {"max_age": 29.5},
        {"min_age": None, "max_age": None, "min_income": None, "citizenship_allowed": None},
        {"min_income": 50000},
        {"min_income": 50001},
        {"citizenship_allowed": "Великое Княжество"},
        {"citizenship_allowed": ["Лесное Ханство"]},
        {"citizenship_allowed": []},
        {"citizenship_allowed": ""},
    ],
)
def test_chroma_filter_matches_pure_filter_on_edges(rules):
    products = [product("p", **rules)]
    eligible, _ = split_by_eligibility(products, HERO)
    assert make_store(products).eligible_ids(HERO) == {p["id"] for p in eligible}


def test_other_catalog_gets_other_key(products):
    changed = [dict(products[0], text="другой текст")] + products[1:]
    assert catalog_key(products) == catalog_key([dict(p) for p in products])
    assert catalog_key(changed) != catalog_key(products)


def test_sessions_do_not_share_collections(products):
    # оба хранилища в одном процессе, как две сессии Streamlit
    first, second = make_store(products), make_store(products[:3])
    assert first.name != second.name
    first.close()
    assert second.count() == 3


def test_collection_is_dropped_with_the_store(products):
    store = make_store(products)
    name = store.name
    import chromadb

    client = chromadb.EphemeralClient(chromadb.config.Settings(anonymized_telemetry=False))
    assert name in [c.name for c in client.list_collections()]
    del store
    assert name not in [c.name for c in client.list_collections()]


def test_no_chromadb_means_no_store(products, monkeypatch):
    monkeypatch.setitem(sys.modules, "chromadb", None)
    assert build_store(products, random_vectors(len(products)), [""] * len(products)) is None


def fake_embed_for(products, vectors):
    by_text = {product_text(p): v for p, v in zip(products, vectors)}
    # вопрос совпадает с первым продуктом
    return lambda texts: [by_text.get(t, vectors[0]) for t in texts]


def test_pipeline_uses_chroma_when_available(products, hero_by_name):
    vectors = random_vectors(len(products))
    store = make_store(products, vectors)
    hero = hero_by_name["Илья Муромец"]
    eligible, _ = split_by_eligibility(products, hero)

    results, method = get_relevant_products(eligible, "вопрос", fake_embed_for(products, vectors), store, hero)
    assert method == METHOD_CHROMA
    assert results[0][0]["id"] == products[0]["id"]


def test_pipeline_falls_back_to_memory_when_chroma_fails(products, hero_by_name):
    class BrokenStore:
        def search(self, *args):
            raise RuntimeError("коллекция пропала")

    vectors = random_vectors(len(products))
    hero = hero_by_name["Илья Муромец"]
    eligible, _ = split_by_eligibility(products, hero)
    _, method = get_relevant_products(eligible, "вопрос", fake_embed_for(products, vectors), BrokenStore(), hero)
    assert method == METHOD_EMBEDDINGS


def test_pipeline_drops_what_pure_filter_rejected(products, hero_by_name, caplog):
    class LeakyStore:
        def search(self, query_vector, hero, threshold, top_k):
            return [(p, 0.9) for p in [rejected[0][0], eligible[0]]]

    hero = hero_by_name["Конь Юлий"]
    eligible, rejected = split_by_eligibility(products, hero)
    vectors = random_vectors(len(products))
    results, _ = get_relevant_products(eligible, "вопрос", fake_embed_for(products, vectors), LeakyStore(), hero)
    assert [p["id"] for p, _ in results] == [eligible[0]["id"]]
    assert "ineligible" in caplog.text
