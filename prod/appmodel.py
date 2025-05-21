from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI # 假设你使用OpenAI模型
from langchain_ollama import OllamaLLM

# 1. 定义你期望的输出数据结构 (Pydantic Model)
class Deposit(BaseModel):
    name: str = Field(description="The name of the person")
    age: Optional[int] = Field(description="The age of the person,if know")
    tx_code: int = Field(description="交易类型，取款交易返回200101,存款交易返回200102")
    occupation: Optional[str] = Field(None, description="The occupation of the person, if known")
    amount: Optional[int] = Field(None, description="交易金额, if known")
    agent: Optional[int] = Field(None, description="是否代替别人办理交易，如果是返回1，不是返回0, if known")
    #hobbies: List[str] = Field(description="A list of hobbies the person has")

# 2. 创建 PydanticOutputParser 实例
parser = PydanticOutputParser(pydantic_object=Deposit)

# 3. 创建 Prompt Template，并注入格式指令
# parser.get_format_instructions() 会生成一个包含 JSON Schema 的字符串
prompt = PromptTemplate(
    template="Extract information about the person mentioned in the text.\n{format_instructions}\nText: {text}",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 4. 初始化 LLM
#llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm = OllamaLLM(model="llama3.1:latest",temperature=0)
#llm = OllamaLLM(model="deepseek-r1:32b",temperature=0)


# 5. 构建链
chain = prompt | llm | parser

# 6. 运行链
#text_to_parse = "John is a 30-year-old software engineer who enjoys hiking and reading."
#text_to_parse = "张三已经50了，在店里来回的逛是个程序员，他喜欢读书和做实验,带着爱人的证件到了银行，代替爱人取款50220元"
text_to_parse = "张三取款50220元"

try:
    parsed_output: Deposit = chain.invoke({"text": text_to_parse})
    print(f"Parsed Name: {parsed_output.name}")
    print(f"Parsed Age: {parsed_output.age}")
    print(f"Parsed Occupation: {parsed_output.occupation}")
    print(f"Paserd txtype: {parsed_output.tx_code}")
    print(f"Paserd agent: {parsed_output.agent}")
    print(f"Paserd amount: {parsed_output.amount}")
    #print(f"Parsed Hobbies: {parsed_output.hobbies}")
except Exception as e:
    print(f"Error parsing LLM output: {e}")