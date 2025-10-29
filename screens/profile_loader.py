# screens/profile_loader.py
import streamlit as st
import json
import os

def show():
    st.title("✨ Сундук Мудрости")
    st.subheader("Добро пожаловать в сказочный финансовый советник Княжеского банка!")

    st.markdown("""
    Чтобы начать, пожалуйста, укажите источник данных о героях:
    
    - Загрузите свой файл `heroes.json`, **ИЛИ**
    - Используйте наши демо-профили (из `data/heroes.json`)
    """)

    # Аккордеон с требованиями к формату JSON
    with st.expander("📘 Требования к кастомному файлу `heroes.json`"):
        st.markdown("""
        Ваш JSON должен быть **массивом объектов**, где каждый герой содержит **обязательные поля**:
        ```json
        [
          {
            "card_suffix": "1234",
            "name": "Соловей-разбойник",
            "age": 35,
            "income": 1200,
            "citizenship": "Лесное Ханство"
          }
        ]
        ```
        **Обязательные поля:**
        - `card_suffix` — строка из **4 цифр** (например, `"1111"`), уникальный идентификатор героя.
        - `name` — имя героя (строка).
        - `age` — возраст (целое число, ≥0).
        - `income` — доход в **золотых** (целое число, ≥0).
        - `citizenship` — гражданство (строка, например `"Княжество"` или `"Лесное Ханство"`).

        Эти поля используются для:
        - Авторизации по 4 цифрам карты,
        - Фильтрации финансовых продуктов по возрасту, доходу и гражданству.
        """)

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🔷 Использовать демо-профили"):
            demo_path = "data/heroes.json"
            if os.path.exists(demo_path):
                try:
                    with open(demo_path, "r", encoding="utf-8") as f:
                        heroes = json.load(f)
                    st.session_state["heroes_data"] = heroes
                    st.success("✅ Демо-профили загружены!")
                except Exception as e:
                    st.error(f"Ошибка чтения демо-файла: {e}")
            else:
                st.error("Файл `data/heroes.json` не найден. Убедитесь, что он существует в папке проекта.")

    with col2:
        uploaded_file = st.file_uploader("Загрузите свой файл с профилями героев", type="json")
        if uploaded_file:
            try:
                heroes = json.load(uploaded_file)
                # Базовая валидация
                if not isinstance(heroes, list):
                    st.error("Файл должен содержать массив героев.")
                elif len(heroes) == 0:
                    st.error("Массив героев пуст.")
                else:
                    # Проверим первый элемент на наличие обязательных полей
                    first = heroes[0]
                    required = {"card_suffix", "name", "age", "income", "citizenship"}
                    if not required.issubset(first.keys()):
                        missing = required - set(first.keys())
                        st.warning(f"⚠️ В герое отсутствуют поля: {missing}. Возможны ошибки при фильтрации.")
                    st.session_state["heroes_data"] = heroes
                    st.success("✅ Ваши профили успешно загружены!")
            except Exception as e:
                st.error(f"Ошибка при чтении JSON: {e}")

    if "heroes_data" in st.session_state:
        st.divider()
        st.info(f"Загружено {len(st.session_state['heroes_data'])} профилей героев.")
        if st.button("➡️ Перейти к авторизации"):
            st.session_state["screen"] = "auth"
            st.rerun()