import streamlit as st

from rag.data import validate_heroes
from screens import data_source
from utils import go, step_header

DEMO_PATH = "data/heroes.json"


def show():
    step_header(
        "profile_loader",
        "Профили героев",
        "Кто может прийти в банк. Возьмите демо-набор или загрузите свой файл.",
    )

    with st.expander("Формат своего `heroes.json`"):
        st.markdown(
            """
Массив объектов, у каждого героя обязательные поля:

```json
[
  {
    "card_suffix": "1234",
    "name": "Соловей-разбойник",
    "age": 40,
    "gender": "мужской",
    "income": 80000,
    "citizenship": "Лесное Ханство",
    "traits": "Талантливый певец, держит таверну на границе"
  }
]
```

- `card_suffix` — 4 цифры строкой, по ним герой входит в банк;
- `age`, `income`, `citizenship` — по ним фильтруются продукты;
- `gender` — необязательное, нужно для обращения («дорогой» / «дорогая»);
- `traits` — необязательное, попадает в промпт, чтобы совет звучал лично.

Файл проверяется целиком: если хоть один герой не подходит под формат, он не загрузится.
            """
        )

    items = data_source.show("heroes_data", DEMO_PATH, validate_heroes, "Использовать демо-профили")
    if items:
        st.success(f"Загружено героев: {len(items)}")
        st.button("Дальше — вход в банк", type="primary", on_click=go, args=("auth",))
