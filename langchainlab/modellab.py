from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template ="""
Question:{question}

Answer:Let's think step by step .
"""

prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model="llama3.1:latest")

chain = prompt|model

print(chain.invoke({"question":"what is langchain"}))