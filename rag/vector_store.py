"""
Векторная база Chroma для каталога продуктов.

База живёт в памяти процесса, у каждой сессии своя коллекция. Все EphemeralClient в одном
процессе делят одно хранилище, поэтому изоляцию дают имена коллекций: случайная часть на
сессию и хэш каталога. Векторы считает наша модель эмбеддингов, своей модели Chroma не грузит.
"""
import hashlib
import json
import logging
import uuid
import weakref

import numpy as np

logger = logging.getLogger(__name__)

# Вместо «без ограничения»: Chroma не умеет искать по отсутствующему полю
NO_LIMIT = 1e12


def catalog_key(products):
    """Короткий хэш каталога: другие данные — другая коллекция."""
    raw = json.dumps(products, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _bound(value, default):
    # числа храним как float: Chroma сравнивает int и float по-разному
    return float(default if value is None else value)


def product_metadata(product):
    rules = product.get("eligibility") or {}
    # пустой список или строка — без ограничения, как в rejection_reason
    allowed = rules.get("citizenship_allowed") or []
    if isinstance(allowed, str):
        allowed = [allowed]
    metadata = {
        "name": product["name"],
        "type": product.get("type") or "",
        "min_age": _bound(rules.get("min_age"), -NO_LIMIT),
        "max_age": _bound(rules.get("max_age"), NO_LIMIT),
        "min_income": _bound(rules.get("min_income"), -NO_LIMIT),
        "citizenship_any": not allowed,
    }
    if allowed:
        metadata["citizenship"] = list(allowed)
    return metadata


def eligibility_where(hero):
    """Те же правила, что в rag.eligibility, но условием where для Chroma."""
    age, income = float(hero["age"]), float(hero["income"])
    return {
        "$and": [
            {"min_age": {"$lte": age}},
            {"max_age": {"$gte": age}},
            {"min_income": {"$lte": income}},
            {"$or": [{"citizenship_any": True}, {"citizenship": {"$contains": hero["citizenship"]}}]},
        ]
    }


def _client():
    """Клиент Chroma или None, если chromadb не установлен."""
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        logger.warning("chromadb is not installed, searching embeddings in memory")
        return None
    # настройки у всех клиентов процесса должны совпадать, иначе Chroma откажет
    return chromadb.EphemeralClient(Settings(anonymized_telemetry=False))


def _drop_collection(client, name):
    try:
        client.delete_collection(name)
    except Exception:
        logger.warning("Failed to delete Chroma collection %s", name, exc_info=True)


class ProductStore:
    """Коллекция с продуктами одного каталога. Удаляется, когда объект больше никому не нужен."""

    def __init__(self, client, products, vectors, documents):
        self.catalog_key = catalog_key(products)
        self.name = f"products-{uuid.uuid4().hex[:12]}-{self.catalog_key}"
        self._products = {p["id"]: p for p in products}
        self._collection = client.create_collection(
            self.name,
            configuration={"hnsw": {"space": "cosine"}},
            embedding_function=None,
        )
        # коллекция живёт столько же, сколько объект: сессия ушла — ушли и данные
        self._finalizer = weakref.finalize(self, _drop_collection, client, self.name)
        self._collection.add(
            ids=list(self._products),
            embeddings=np.asarray(vectors, dtype=np.float32),
            documents=list(documents),
            metadatas=[product_metadata(p) for p in products],
        )

    def count(self):
        return self._collection.count()

    def peek(self, limit=5):
        """Несколько записей как они лежат в базе: id, текст, метаданные."""
        got = self._collection.get(limit=limit, include=["documents", "metadatas"])
        return [
            {"id": i, "document": d, "metadata": m}
            for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])
        ]

    def eligible_ids(self, hero):
        """Что пропускает фильтр Chroma; нужно, чтобы сверить его с rag.eligibility."""
        return set(self._collection.get(where=eligibility_where(hero), include=[])["ids"])

    def search(self, query_vector, hero, threshold, top_k):
        """
        Ближайшие продукты, которые герою положены, парами (продукт, сходство).

        В пространстве cosine Chroma отдаёт расстояние 1 − cos, обратно переводим в сходство,
        чтобы порог значил то же, что и при поиске в памяти.
        """
        result = self._collection.query(
            query_embeddings=np.asarray([query_vector], dtype=np.float32),
            n_results=top_k,
            where=eligibility_where(hero),
            include=["distances"],
        )
        pairs = [(self._products[i], 1.0 - d) for i, d in zip(result["ids"][0], result["distances"][0])]
        return [(p, s) for p, s in pairs if s >= threshold]

    def close(self):
        self._finalizer()


def build_store(products, vectors, documents):
    """Новая коллекция с каталогом или None, если Chroma недоступна."""
    client = _client()
    if client is None:
        return None
    try:
        return ProductStore(client, products, vectors, documents)
    except Exception:
        logger.exception("Failed to build Chroma collection")
        return None
