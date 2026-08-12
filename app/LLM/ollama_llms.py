from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from personality.friday_personality import personality


llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0.7
)

user_prompt = input("YOU : ")

messages = [
    SystemMessage(content=personality),
    HumanMessage(content=user_prompt)
]

print("AI: ", end="", flush=True)

for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)