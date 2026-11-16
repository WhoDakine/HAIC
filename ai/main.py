
from ollama_prompt import ask_ai

print("Hawaii Legislative Assistance Chatbot")
print("Type 'exit' to quit.")

while True:

    question = input("\nStart chatting here: ")

    if question.lower() == "exit":
        break

    answer = ask_ai(question)

    print("\nFred:")
    print(answer)
