import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/ask")


st.set_page_config(page_title="Bank Policy RAG Copilot", layout="wide")

st.title("Bank Policy RAG Copilot")
st.caption("Internal AI assistant with RAG, citations, guardrails, human review and LLM-as-a-Judge.")

question = st.text_area(
    "Ask a banking policy question",
    placeholder="Какие документы нужны ИП для открытия расчётного счёта?",
    height=120,
)

if st.button("Ask Copilot", type="primary"):
    if not question.strip():
        st.warning("Введите вопрос перед отправкой.")
    else:
        payload = {
            "user_id": "demo_employee",
            "question": question,
            "channel": "streamlit_demo",
        }
        try:
            res = requests.post(API_URL, json=payload, timeout=120)
            res.raise_for_status()
            data = res.json()
        except requests.RequestException as e:
            st.error(f"Не удалось получить ответ от API: {e}")
            st.stop()

        status_color = {
            "answered": "green",
            "needs_human_review": "orange",
            "refused": "red",
        }.get(data.get("status"), "gray")
        st.markdown(f"**Status:** :{status_color}[{data.get('status')}]")

        st.subheader("Answer")
        st.write(data.get("answer", ""))

        st.subheader("Risk & Judge")
        st.json({"risk": data.get("risk"), "judge_score": data.get("judge_score")})

        st.subheader("Sources")
        sources = data.get("sources", []) or []
        if not sources:
            st.info("Источники не использовались (отказ или эскалация).")
        for source in sources:
            with st.expander(f"{source['source']} (score={source.get('score')})"):
                st.write(source["content"])
