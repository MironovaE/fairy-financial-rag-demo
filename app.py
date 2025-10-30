# app.py
# streamlit run app.py
import streamlit as st

st.set_page_config(
    page_title="Fairy Financial RAG Demo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Импорт экранов
from screens.intro import show as show_intro
from screens.profile_loader import show as show_profile_loader
from screens.auth import show as show_auth
from screens.query_input import show as show_query_input
from screens.product_loader import show as show_product_loader
from screens.preprocessing import show as show_preprocessing
from screens.rag_simulation import show as show_rag_simulation
from screens.llm_response import show as show_llm_response

# Инициализация состояния экрана
if "screen" not in st.session_state:
    st.session_state["screen"] = "intro"

# Навигация
current_screen = st.session_state["screen"]

# Навигация по состоянию сессии
if current_screen == "intro":
    # Шаг 0: презентация intro
    show_intro()
elif current_screen == "profile_loader":
    # Шаг 1: Загрузка данных о героях
    show_profile_loader()
elif current_screen == "auth":
    # Шаг 2: Авторизация по карте
    show_auth()
elif current_screen == "query_input":
    # Шаг 3: Ввод финансового запроса
    show_query_input()
elif current_screen == "product_loader":
    # Шаг 4: Загрузка данных о продуктах
    show_product_loader()
elif current_screen == "preprocessing":
    # Шаг 4: Препроцессинг - фильтрация базы
    show_preprocessing()
elif current_screen == "rag_simulation":
    # Шаг 6: RAG-имитация — семантический отбор и формирование промпта
    show_rag_simulation()
elif current_screen == "llm_response":
    # Шаг 7: Генерация и показ финального ответа от LLM (пока мок)
    show_llm_response()
else:
    # На случай ошибки — возврат к началу
    st.session_state["screen"] = "profile_loader"
    st.rerun()