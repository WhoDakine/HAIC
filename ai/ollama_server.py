
import os
import hmac
import ollama

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


MODEL = "qwen3:4b"

API_KEY = os.getenv("LEI_API_KEY")

if not API_KEY:
    raise RuntimeError("LEI_API_KEY environment variable is missing.")

client = ollama.Client(host="http://localhost:11434")

app = FastAPI()


SYSTEM_PROMPT = """
You are a government assistance research
assistant specializing in Hawaii.

Your users are Hawaii state and local legislators.

Your responsibilities:
- Analyze district demographic information.
- Identify relevant federal assistance programs.
- Identify relevant Hawaii state assistance programs.
- Explain program eligibility requirements.
- Explain potential benefits to communities.
- Identify missing information.

IMPORTANT RULES:

1. Use the provided government data as your
   primary source of information.

2. Never invent statistics, funding amounts,
   eligibility requirements, or programs.

3. Never claim that a district qualifies for a
   program without sufficient evidence.

4. Distinguish potential eligibility from
   confirmed eligibility.

5. If information is missing, say so.

6. Do not fabricate citations or URLs.
"""


class ChatRequest(BaseModel):
    question: str
    government_data: str = "No government data provided."


@app.get("/health")
def health():
    return {"status": "online"}


@app.post("/chat")
def chat(
    request: ChatRequest,
    authorization: str = Header(default="")
):

    expected = f"Bearer {API_KEY}"

    if not hmac.compare_digest(authorization, expected):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
                GOVERNMENT DATA:
                {request.government_data}

                USER QUESTION:
                {request.question}
                """
            }
        ]
    )

    return {
        "answer": response.message.content
    }
