
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.main import answer_question


st.set_page_config(
    page_title="Legislative Engineered Intelligence",
    page_icon=str(Path(__file__).with_name("lei-icon.svg")),
    layout="centered"
)

st.markdown(
    """
    <style>
    @import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap");

    :root {
        color-scheme: dark;
        --ink: #e5e9e3;
        --muted: #aab5ae;
        --paper: #171f1d;
        --paper-light: #202a27;
        --field: #26332e;
        --field-hover: #34443d;
        --line: #3c4b44;
        --forest: #527869;
        --forest-deep: #3e6255;
        --coral: #e2a083;
    }

    .stApp,
    [data-testid="stMain"],
    [data-testid="stAppViewContainer"] {
        background: var(--paper) !important;
        color: var(--ink) !important;
        font-family: "DM Sans", "Segoe UI", sans-serif;
    }

    [data-testid="stHeader"] {
        background: var(--paper) !important;
        border-bottom: 1px solid var(--line);
    }

    [data-testid="stMainMenu"] {
        display: none;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 820px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--ink) !important;
        font-family: "Newsreader", Georgia, serif !important;
        font-weight: 400 !important;
    }

    .stApp p,
    .stApp label,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stWidgetLabel"] * {
        color: var(--ink) !important;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {
        color: var(--muted) !important;
    }

    .stApp a {
        color: var(--coral) !important;
    }

    [data-testid="stAlertContentError"] [data-testid="stMarkdownContainer"],
    [data-testid="stAlertContentError"] [data-testid="stMarkdownContainer"] * {
        color: #2f2d2b !important;
    }

    [data-testid="stSidebar"] {
        background: #1c2622 !important;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: "Newsreader", Georgia, serif !important;
    }

    [data-testid="stForm"] {
        padding: 1.5rem;
        background: var(--paper-light) !important;
        border: 1px solid var(--line) !important;
    }

    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div,
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] [data-baseweb="textarea"] > div {
        background: var(--field) !important;
        border: 1px solid var(--line) !important;
        border-radius: 3px !important;
        box-shadow: none !important;
    }

    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] input,
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--ink) !important;
        font-family: "DM Sans", "Segoe UI", sans-serif;
    }

    [data-baseweb="select"] div,
    [data-baseweb="select"] span {
        color: var(--ink) !important;
    }

    [data-testid="stTextArea"] textarea {
        color: #2f2d2b !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: var(--muted) !important;
        opacity: 1;
    }

    [data-baseweb="input"]:focus-within > div,
    [data-baseweb="textarea"]:focus-within > div,
    [data-baseweb="select"]:focus-within > div,
    [data-testid="stChatInput"]:focus-within > div {
        border-color: var(--forest) !important;
        box-shadow: 0 0 0 1px var(--forest) !important;
    }

    [data-testid="stNumberInput"] button {
        background: var(--field) !important;
        color: var(--muted) !important;
        border-color: var(--line) !important;
    }

    [data-baseweb="popover"] {
        background: var(--paper-light) !important;
    }

    [role="option"] {
        background: var(--paper-light) !important;
        color: var(--ink) !important;
    }

    [role="option"]:hover {
        background: var(--field) !important;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        min-height: 2.6rem;
        border: 1px solid var(--line) !important;
        border-radius: 0 !important;
        background: var(--field) !important;
        color: var(--ink) !important;
        font-family: "DM Sans", "Segoe UI", sans-serif;
        font-weight: 600;
        transition: background .2s, color .2s, border-color .2s;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--forest) !important;
        background: var(--field-hover) !important;
        color: var(--ink) !important;
    }

    .stFormSubmitButton > button {
        border-color: var(--forest) !important;
        background: var(--forest) !important;
        color: var(--ink) !important;
    }

    .stFormSubmitButton > button:hover {
        border-color: var(--forest-deep) !important;
        background: var(--forest-deep) !important;
        color: var(--ink) !important;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid var(--line) !important;
        border-radius: 3px !important;
        background: var(--paper-light) !important;
    }

    [data-testid="stChatInput"] {
        background: transparent !important;
    }

    [data-testid="stBottom"] > div {
        background: var(--paper-light) !important;
    }

    hr {
        border-color: var(--line) !important;
    }

    .lei-chat-title {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .lei-chat-title h1 {
        margin: 0;
        color: var(--ink);
        font-size: 2rem;
        line-height: 1.2;
    }

    .lei-chat-title-mark {
        width: 34px;
        height: 34px;
        flex: 0 0 34px;
        display: grid;
        place-items: center;
        border: 1px solid var(--coral);
        border-radius: 50%;
        color: var(--coral);
        font-family: "DM Sans", "Segoe UI", sans-serif;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: .03em;
    }
    </style>
    """,
    unsafe_allow_html=True
)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "legislator" not in st.session_state:
    st.session_state.legislator = None


# Header
st.markdown(
    '<div class="lei-chat-title"><span class="lei-chat-title-mark" aria-hidden="true">LEI</span>'
    '<h1>Legislative Engineered Intelligence</h1></div>',
    unsafe_allow_html=True
)

st.caption(
    "Government assistance research assistant"
)


# Sidebar
with st.sidebar:

    st.header("Conversation")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

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


# Legislator Profile
if st.session_state.legislator is None:

    st.header("Legislator Profile")

    with st.form("legislator_profile"):

        name = st.text_input("Full Name")

        chamber = st.selectbox(
            "Legislative Chamber",
            ["House", "Senate"]
        )

        if chamber == "House":
            district = st.number_input(
                "House District",
                min_value=1,
                max_value=51,
                value=1
            )
        else:
            district = st.number_input(
                "Senate District",
                min_value=1,
                max_value=25,
                value=1
            )

        position = st.text_input(
            "Position / Committee"
        )

        policy_interests = st.text_area(
            "Policy Interests",
            placeholder=(
                "Example: housing, education, "
                "transportation, public health"
            )
        )

        submitted = st.form_submit_button(
            "Continue to Chatbot"
        )

        if submitted:

            if not name.strip():
                st.error("Please enter your name.")

            else:

                st.session_state.legislator = {
                    "name": name,
                    "chamber": chamber,
                    "district": int(district),
                    "position": position,
                    "policy_interests": policy_interests
                }

                st.rerun()


# Chatbot
else:

    legislator = st.session_state.legislator

    st.subheader(
        f"Welcome, {legislator['name']}"
    )

    st.caption(
        f"{legislator['chamber']} District "
        f"{legislator['district']}"
    )

    if st.button("Change Legislator Profile"):
        st.session_state.legislator = None
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input(
        "Ask about government assistance programs..."
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing district data and assistance programs..."
            ):

                try:

                    result = answer_question(
                        legislator,
                        prompt
                    )

                    answer = result["response"]

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                    with st.expander(
                        "View government data used"
                    ):

                        st.json(
                            result["government_data"]
                        )

                except Exception as error:

                    st.error(
                        f"An error occurred: {error}"
                    )
