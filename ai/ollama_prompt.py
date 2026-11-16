
import ollama

MODEL = "qwen3:4b"

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


def ask_ai(question, government_data="No government data provided."):

    response = ollama.chat(
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
                {government_data}

                USER QUESTION:
                {question}
                """
            }
        ]
    )

    return response.message.content
