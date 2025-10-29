# screens/llm_response.py
import streamlit as st
from groq import Groq
from utils import get_address_and_verb  # ← используем ту же логику, что и в RAG

def call_groq(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ← оптимальная модель для free tier
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,  # достаточно для 4–5 сказочных предложений
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Сундук Мудрости не смог связаться с волшебным кристаллом Groq:\n\n_{str(e)[:150]}..._\n\nНо не отчаивайся! Вот мудрый совет от самого Сундука:"

def mock_response(hero, query):
    # Используем ту же функцию, что и в промпте — полная согласованность!
    address, verb = get_address_and_verb(hero)
    eligible_products = st.session_state.get("eligible_products", [])

    base = f"{address.capitalize()}! Ты {verb} с важным вопросом: «{query}». Увы, волшебный кристалл Groq сегодня устал. Но не беда! Сундук Мудрости всегда найдёт выход."

    if eligible_products:
        product = eligible_products[0]
        suggestion = f"\n\n👆 Вот мой мудрый совет:\n**{product['name']}** — {product.get('description', 'то, что тебе нужно')}."
    else:
        suggestion = "\n\nПока я не нашёл продуктов, подходящих под твой профиль. Попробуй уточнить цель — например: «Хочу накопить на терем» или «Нужен заем на коня»."

    final = f"{base}{suggestion}\n\nА если хочешь больше — обратись к Князю, он всезнающ и мудр.👆"
    return final

def show():
    st.title("🧙 Сундук Мудрости отвечает")

    hero = st.session_state["hero"]
    query = st.session_state.get("user_query", "Не указана")

    st.markdown(f"**Герой:** {hero.get('name', '—')}")
    st.markdown(f"**Цель:** _«{query}»_")
    st.divider()

    if "llm_response" not in st.session_state:
        with st.spinner("Сундук Мудрости обращается к волшебному кристаллу Groq..."):
            prompt = st.session_state["final_prompt"]
            response = call_groq(prompt)
            # Если ответ содержит ошибку — добавляем мок
            if response and "⚠️ Сундук Мудрости не смог" in response:
                response += "\n\n" + mock_response(hero, query)
            elif not response:
                # Если response = None (редко, но возможно)
                response = mock_response(hero, query)
            st.session_state["llm_response"] = response

    st.subheader("💬 Совет Сундука Мудрости")
    st.markdown(f"> {st.session_state['llm_response']}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Вернуться к RAG"):
            st.session_state["screen"] = "rag_simulation"
            st.rerun()
    with col2:
        if st.button("🔄 Начать заново"):
            st.session_state.clear()
            st.rerun()