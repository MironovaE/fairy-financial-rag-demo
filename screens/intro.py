from pathlib import Path

import streamlit as st

from utils import go

CHEST_IMAGE = Path(__file__).resolve().parent.parent / "assets" / "wisdom-chest.png"

CHAPTERS = (
    ("I", "Представься", "Выбери героя или загрузи свой профиль."),
    ("II", "Загадай цель", "Сундук проверит правила банка и найдёт подходящие продукты."),
    ("III", "Получай совет", "Увидишь найденное, промпт и ответ модели."),
)


def show():
    st.markdown('<p class="fairy-kicker">Княжеский банк · сказка с проверяемой начинкой</p>', unsafe_allow_html=True)

    copy, art = st.columns([1.15, 1], gap="large")
    with copy:
        st.title("Сундук Мудрости")
        st.markdown(
            '<p class="fairy-lead">Расскажи, на что копишь или что хочешь устроить. '
            'Сундук сверит правила банка, пороется в каталоге и подберёт совет. '
            'Юлию пенсионный счёт пока не полагается — даже если он убедительно попросит.</p>',
            unsafe_allow_html=True,
        )
        st.button("Начать", type="primary", on_click=go, args=("profile_loader",))
        st.markdown(
            '<p class="fairy-aside">Все герои и продукты выдуманы. На каждом шаге можно посмотреть, '
            'как устроено «волшебство».</p>',
            unsafe_allow_html=True,
        )
    with art:
        st.image(str(CHEST_IMAGE), use_column_width=True)

    st.markdown('<p class="fairy-section-label">Три главы одного приключения</p>', unsafe_allow_html=True)
    for column, (number, title, description) in zip(st.columns(3, gap="medium"), CHAPTERS):
        with column:
            st.markdown(
                f'<div class="fairy-chapter"><span class="fairy-chapter-num">{number}</span>'
                f'<h3 class="fairy-chapter-title">{title}</h3>'
                f'<p class="fairy-chapter-text">{description}</p></div>',
                unsafe_allow_html=True,
            )

    with st.expander("Как работает сказка — шаг за шагом"):
        st.markdown(
            """
1. Герой входит по последним четырём цифрам карты.
2. Сундук берёт его вопрос и каталог продуктов.
3. Фильтр по возрасту, доходу и гражданству убирает то, что герою не положено. Это происходит до поиска.
4. Семантический поиск находит пять похожих продуктов: сначала Chroma и эмбеддинги, затем запасные
   пути — эмбеддинги в памяти, TF-IDF или ключевые слова.
5. В промпт попадают только подходящие продукты и черты героя. Ответ формулирует модель через Groq;
   если API недоступен, показывается шаблонный ответ с явной пометкой.

Модель эмбеддингов и векторы каталога кэшируются. У каждой сессии своя коллекция Chroma в памяти;
при новом каталоге она собирается заново.
            """
        )
