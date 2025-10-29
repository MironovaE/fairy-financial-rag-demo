# screens/query_input.py
import streamlit as st

def show():
    hero = st.session_state.get("hero", {})
    hero_name = hero.get("name", "добрый путник")

    # Кнопка "Выйти" в правом верхнем углу
    col_empty, col_exit = st.columns([6, 1])
    with col_exit:
        if st.button("🚪 Выйти", key="exit_from_query"):
            st.session_state.clear()
            st.rerun()

    st.title("🏦 Сундук Мудрости")
    st.markdown("*Сказочный финансовый советник Княжеского банка*")

    # Приветствие
    st.markdown(f"""
    <div style="font-size: 1.2em; line-height: 1.6;">
    🌟 <b>Приветствуем тебя, {hero_name}!</b><br>
    Добро пожаловать в Княжеский банк — место, где золотые мечты превращаются в реальность!<br>
    Расскажи, какую финансовую цель ты хочешь достичь? Может, накопить на терем на Мальдивах?<br>
    Или собрать сбережения на Княжеский пир мечты?
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Поле ввода — ОБЯЗАТЕЛЬНО с key="user_query_input"
    st.text_area(
        "Задайте свой вопрос Сундуку Мудрости:",
        placeholder="Например: «Как накопить на терем на Мальдивах за 2 месяца?»",
        height=100,
        key="user_query_input"
    )

    # Получаем текст из поля
    user_query = st.session_state.get("user_query_input", "").strip()

    # Кнопка отправки
    if st.button("➤ Получить совет"):
        if user_query:
            # Сохраняем запрос
            st.session_state["user_query"] = user_query
            # Говорим: "Теперь показывай экран загрузки продуктов"
            st.session_state["screen"] = "product_loader"
            # Обновляем страницу
            st.rerun()
        else:
            st.error("Пожалуйста, напишите свой вопрос!")