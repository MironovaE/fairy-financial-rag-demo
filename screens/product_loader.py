import json

import streamlit as st

from utils import go, step_header

DEMO_PATH = "data/products.json"
REQUIRED_FIELDS = {"id", "name", "description", "text", "eligibility"}


def load_demo():
    with open(DEMO_PATH, encoding="utf-8") as f:
        st.session_state["products_data"] = json.load(f)


def show():
    step_header(
        "product_loader",
        "Продукты банка",
        "Из чего Сундук будет выбирать. Возьмите демо-набор или загрузите свой файл.",
    )

    with st.expander("Формат своего `products.json`"):
        st.markdown(
            """
Массив объектов, у каждого продукта обязательные поля:

```json
[
  {
    "id": "deposit_golden_acorn",
    "name": "Вклад «Золотой Жёлудь»",
    "type": "deposit",
    "description": "Короткое описание — попадёт в промпт",
    "text": "Полный текст — по нему идёт семантический поиск",
    "eligibility": {
      "min_age": 18,
      "max_age": null,
      "min_income": 50000,
      "citizenship_allowed": ["Великое Княжество"]
    }
  }
]
```

Все поля внутри `eligibility` необязательны: `null` или отсутствие поля означает «без ограничения».
            """
        )

    st.button("Использовать демо-продукты", on_click=load_demo)

    uploaded_file = st.file_uploader("Или загрузите свой файл", type="json")
    if uploaded_file:
        try:
            products = json.load(uploaded_file)
        except json.JSONDecodeError as e:
            st.error(f"Не получилось прочитать JSON: {e}")
        else:
            if not isinstance(products, list) or not products:
                st.error("В файле должен быть непустой массив продуктов.")
            else:
                missing = REQUIRED_FIELDS - set(products[0])
                if missing:
                    st.warning(f"У первого продукта не хватает полей: {', '.join(sorted(missing))}.")
                st.session_state["products_data"] = products

    if "products_data" in st.session_state:
        st.success(f"Загружено продуктов: {len(st.session_state['products_data'])}")
        st.button("Дальше — фильтрация", type="primary", on_click=go, args=("preprocessing",))
