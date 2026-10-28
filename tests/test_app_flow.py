import pytest
from streamlit.testing.v1 import AppTest

from conftest import ROOT
from rag import embedder


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()
    assert not at.exception, at.exception


@pytest.fixture
def app(monkeypatch):
    # без модели эмбеддингов и без ключа Groq: проверяем запасные пути, сеть не нужна
    monkeypatch.setattr(embedder, "load_model", lambda: None)
    monkeypatch.chdir(ROOT)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.secrets["GROQ_API_KEY"] = ""
    at.run()
    assert not at.exception, at.exception
    return at


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


def test_unknown_card(app):
    click(app, "Начать")
    click(app, "Использовать демо-профили")
    click(app, "Дальше — вход в банк")
    app.text_input[0].input("4321")
    app.button[0].click().run()
    assert "Героя с такой картой нет" in app.error[0].value
