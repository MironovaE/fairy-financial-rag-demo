import json

import streamlit as st

from utils import go, step_header

DEMO_PATH = "data/heroes.json"
REQUIRED_FIELDS = {"card_suffix", "name", "age", "income", "citizenship"}


def load_demo():
    with open(DEMO_PATH, encoding="utf-8") as f:
        st.session_state["heroes_data"] = json.load(f)


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
    "citizenship": "Лесное Ханство"
  }
]
```

- `card_suffix` — 4 цифры строкой, по ним герой входит в банк;
- `age`, `income`, `citizenship` — по ним фильтруются продукты;
- `gender` — необязательное, нужно для обращения («дорогой» / «дорогая»).
            """
        )

    st.button("Использовать демо-профили", on_click=load_demo)

    uploaded_file = st.file_uploader("Или загрузите свой файл", type="json")
    if uploaded_file:
        try:
            heroes = json.load(uploaded_file)
        except json.JSONDecodeError as e:
            st.error(f"Не получилось прочитать JSON: {e}")
        else:
            if not isinstance(heroes, list) or not heroes:
                st.error("В файле должен быть непустой массив героев.")
            else:
                missing = REQUIRED_FIELDS - set(heroes[0])
                if missing:
                    st.warning(f"У первого героя не хватает полей: {', '.join(sorted(missing))}.")
                st.session_state["heroes_data"] = heroes

    if "heroes_data" in st.session_state:
        st.success(f"Загружено героев: {len(st.session_state['heroes_data'])}")
        st.button("Дальше — вход в банк", type="primary", on_click=go, args=("auth",))
