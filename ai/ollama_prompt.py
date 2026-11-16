
import requests
import streamlit as st

API_URL = st.secrets["OLLAMA_API_URL"].rstrip("/")
API_KEY = st.secrets["LEI_API_KEY"]


def ask_ai(question, government_data="No government data provided."):
    response = requests.post(
        f"{API_URL}/chat",
        headers={
            "Authorization": f"Bearer {API_KEY}"
        },
        json={
            "question": question,
            "government_data": government_data
        },
        timeout=(10, 300)
    )

    response.raise_for_status()

    return response.json()["answer"]
