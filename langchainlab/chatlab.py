from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage,SystemMessage

messages=[
    SystemMessage("Translate the following from English into Chinese"),
    HumanMessage("hi,please introduce youself"),
]

model = OllamaLLM(model="llama3.1:latest")
model.invoke([HumanMessage("what 's llama")])
for token in model.stream(messages):
    print(token.content,end="|")
# print(model.invoke(messages))