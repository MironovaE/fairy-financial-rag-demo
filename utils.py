import streamlit as st

STEPS = [
    "profile_loader",
    "auth",
    "query_input",
    "product_loader",
    "preprocessing",
    "rag_simulation",
    "llm_response",
]


def go(screen):
    st.session_state["screen"] = screen


def restart():
    st.session_state.clear()


def step_header(screen, title, subtitle=None):
    step = STEPS.index(screen) + 1
    st.caption(f"Шаг {step} из {len(STEPS)}")
    st.progress(step / len(STEPS))
    st.title(title)
    if subtitle:
        st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)


def capitalize_first(text):
    # str.capitalize() опускает остальные буквы: «Бабуля Агафья» превратилась бы в «бабуля агафья»
    return text[:1].upper() + text[1:]


def get_address_and_verb(hero):
    """
    Возвращает обращение и глагол в прошедшем времени по полю 'gender' героя.
    """
    name = hero["name"]
    if hero.get("gender") == "женский":
        return f"дорогая {name}", "обратилась"
    return f"дорогой {name}", "обратился"


def hero_summary(hero):
    return f"{hero['name']}, {hero['age']} лет, доход {hero['income']} золотых, {hero['citizenship']}"
