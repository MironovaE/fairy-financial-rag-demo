# screens/product_loader.py
import streamlit as st
import json
import os

def show():
    st.title("✨ Сундук Мудрости")
    st.subheader("Загрузка сказочных финансовых продуктов")

    st.markdown("""
    Чтобы Сундук Мудрости мог подобрать тебе подходящие предложения, укажи источник данных о продуктах Княжеского банка:
    
    - Загрузи свой файл `products.json`, **ИЛИ**
    - Используй нашу демо-базу (из `data/products.json`)
    """)

    # Аккордеон с требованиями к формату JSON
    with st.expander("📘 Требования к кастомному файлу `products.json`"):
        st.markdown("""
        Ваш JSON должен быть **массивом объектов**, где каждый продукт содержит **обязательные поля**:
        ```json
        [
          {
            "id": "unique_product_id",
            "name": "Название продукта",
            "description": "Краткое описание",
            "text": "Полный текст для семантического поиска",
            "eligibility": {
              "min_age": 18,
              "max_age": null,
              "min_income": 50000,
              "citizenship_allowed": ["Великое Княжество", "Лесное Ханство"]
            }
          }
        ]
        ```

        **Обязательные поля:**
        - `id` — уникальный идентификатор (строка),
        - `name` — название продукта (строка),
        - `description` — краткое описание (строка),
        - `text` — полный текст для RAG-поиска (строка),
        - `eligibility` — объект с правилами фильтрации.

        **Поля внутри `eligibility` (все опциональны, но хотя бы одно рекомендуется):**
        - `min_age` — минимальный возраст (целое число или `null`),
        - `max_age` — максимальный возраст (целое число или `null`),
        - `min_income` — минимальный доход в золотых (целое число или `null`),
        - `citizenship_allowed` — массив разрешённых гражданств (массив строк).

        Эти данные используются для:
        - Фильтрации продуктов по профилю героя,
        - Семантического поиска через эмбеддинги (`text`).
        """)

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🔷 Использовать демо-продукты"):
            demo_path = "data/products.json"
            if os.path.exists(demo_path):
                try:
                    with open(demo_path, "r", encoding="utf-8") as f:
                        products = json.load(f)
                    st.session_state["products_data"] = products
                    st.success("✅ Демо-продукты загружены!")
                except Exception as e:
                    st.error(f"Ошибка чтения демо-файла: {e}")
            else:
                st.error("Файл `data/products.json` не найден. Убедитесь, что он существует в папке проекта.")

    with col2:
        uploaded_file = st.file_uploader("Загрузите свой файл с финансовыми продуктами", type="json")
        if uploaded_file:
            try:
                products = json.load(uploaded_file)
                # Базовая валидация
                if not isinstance(products, list):
                    st.error("Файл должен содержать массив продуктов.")
                elif len(products) == 0:
                    st.error("Массив продуктов пуст.")
                else:
                    # Проверим первый элемент на наличие обязательных полей
                    first = products[0]
                    required = {"id", "name", "description", "text", "eligibility"}
                    if not required.issubset(first.keys()):
                        missing = required - set(first.keys())
                        st.warning(f"⚠️ В первом продукте отсутствуют поля: {missing}. Возможны ошибки при фильтрации или RAG-поиске.")
                    st.session_state["products_data"] = products
                    st.success("✅ Твои продукты успешно загружены!")
            except Exception as e:
                st.error(f"Ошибка при чтении JSON: {e}")

    if "products_data" in st.session_state:
        st.divider()
        st.info(f"Загружено {len(st.session_state['products_data'])} сказочных финансовых продуктов.")
        if st.button("➡️ Перейти к анализу данных"):
            st.session_state["screen"] = "preprocessing"
            st.rerun()