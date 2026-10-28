import streamlit as st

from rag.data import validate_products
from screens import data_source
from utils import Key, go, step_header

DEMO_PATH = "data/products.json"


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
`type` тоже необязателен, но без него продукт не найдётся поиском по ключевым словам.
Файл проверяется целиком: если хоть один продукт не подходит под формат, он не загрузится.
            """
        )

    items = data_source.show(Key.PRODUCTS, DEMO_PATH, validate_products, "Использовать демо-продукты")
    if items:
        st.success(f"Загружено продуктов: {len(items)}")
        st.button("Дальше — фильтрация", type="primary", on_click=go, args=("preprocessing",))
