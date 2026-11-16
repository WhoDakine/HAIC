
import streamlit as st
import ollama
import json

from ollama_prompt import MODEL, SYSTEM_PROMPT

# Page configuration
st.set_page_config(
    page_title="Hawaii Legislative AI",
    page_icon="🏛️",
    layout="centered"
)

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("🏛️ Hawaii Legislative AI")
st.caption("Government assistance research assistant")

# Sidebar
with st.sidebar:
    st.header("Conversation")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    # Export conversation
    transcript = "\n\n".join(
        f"{msg['role'].upper()}:\n{msg['content']}"
        for msg in st.session_state.messages
    )

    st.download_button(
        label="📥 Export conversation",
        data=transcript,
        file_name="legislative_chat.txt",
        mime="text/plain",
        disabled=len(st.session_state.messages) == 0
    )

# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask about government assistance programs...")

if prompt:

    # Save and display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("Analyzing your question..."):

            try:
                response = ollama.chat(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        }
                    ] + st.session_state.messages
                )

                answer = response.message.content

                st.markdown(answer)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error(f"An error occurred: {error}")
