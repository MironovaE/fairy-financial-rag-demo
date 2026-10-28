import zlib

import numpy as np
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from conftest import ROOT
from rag import embedder
from rag.vector_store import catalog_key
from utils import Key


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()
    assert not at.exception, at.exception


def start_app(monkeypatch):
    # кэши Streamlit живут в процессе и пережили бы подмену модели из другого теста
    st.cache_resource.clear()
    st.cache_data.clear()
    monkeypatch.chdir(ROOT)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.secrets["GROQ_API_KEY"] = ""
    at.run()
    assert not at.exception, at.exception
    return at


def trigram_encode(model, texts):
    """Вместо настоящей модели: мешок буквенных триграмм, сеть и torch не нужны."""
    vectors = np.zeros((len(texts), 512))
    for row, text in enumerate(texts):
        text = text.lower()
        for i in range(len(text) - 2):
            vectors[row, zlib.crc32(text[i : i + 3].encode()) % 512] += 1
    return vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-9)


@pytest.fixture
def app(monkeypatch):
    # без модели эмбеддингов и без ключа Groq: проверяем запасные пути, сеть не нужна
    monkeypatch.setattr(embedder, "load_model", lambda: None)
    return start_app(monkeypatch)


@pytest.fixture
def app_with_model(monkeypatch):
    pytest.importorskip("chromadb")
    monkeypatch.setattr(embedder, "load_model", lambda: "модель")
    monkeypatch.setattr(embedder, "encode", trigram_encode)
    return start_app(monkeypatch)


def test_main_flow_without_model_and_api(app):
    click(app, "Начать")
    click(app, "Использовать демо-профили")
    click(app, "Дальше — вход в банк")

    app.text_input[0].input("12ab")
    app.button[0].click().run()
    assert app.error[0].value == "Нужно ровно 4 цифры."

    app.text_input[0].input("3333")
    app.button[0].click().run()
    assert app.title[0].value == "Здравствуй, Илья Муромец!"

    app.text_area[0].input("Нужен заём на нового коня")
    app.button[0].click().run()
    click(app, "Использовать демо-продукты")
    click(app, "Дальше — фильтрация")
    click(app, "Дальше — поиск")
    assert any("TF-IDF" in m.value for m in app.markdown)
    assert "Нужен заём на нового коня" in app.code[0].value

    click(app, "Спросить Сундук")
    assert app.title[0].value == "Совет Сундука"
    assert any(m.value.startswith("Дорогой Илья Муромец, ты обратился") for m in app.markdown)
    assert "шаблонный ответ" in app.caption[-1].value


def test_search_goes_through_chroma(app_with_model, products):
    app = app_with_model
    click(app, "Начать")
    click(app, "Использовать демо-профили")
    click(app, "Дальше — вход в банк")
    app.text_input[0].input("7777")
    app.button[0].click().run()
    app.text_area[0].input("Как отложить на старость?")
    app.button[0].click().run()
    click(app, "Использовать демо-продукты")
    click(app, "Дальше — фильтрация")
    click(app, "Дальше — поиск")

    assert any("векторная база Chroma" in m.value for m in app.markdown)
    assert any(e.label == "Что лежит в векторной базе" for e in app.expander)
    key, store = app.session_state[Key.STORE]
    assert key == catalog_key(products)
    assert store.count() == len(products)

    # другой каталог в той же сессии: коллекция пересобирается, старая удаляется
    app.session_state[Key.PRODUCTS] = products[:5]
    app.run()
    new_key, new_store = app.session_state[Key.STORE]
    assert new_key == catalog_key(products[:5])
    assert new_store.count() == 5
    assert not store._finalizer.alive

    click(app, "Спросить Сундук")
    assert any(m.value.startswith("Дорогая Бабуля Агафья, ты обратилась") for m in app.markdown)
    assert "шаблонный ответ" in app.caption[-1].value


def test_unknown_card(app):
    click(app, "Начать")
    click(app, "Использовать демо-профили")
    click(app, "Дальше — вход в банк")
    app.text_input[0].input("4321")
    app.button[0].click().run()
    assert "Героя с такой картой нет" in app.error[0].value
