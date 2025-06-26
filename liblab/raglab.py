# rag_query.py

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama # 或者你使用的其他LLM，如ChatOpenAI
from langchain.chains import RetrievalQA
import os # 用于检查文件/文件夹是否存在

# --- 配置 ---
faiss_index_path = "faiss_index"
embedding_model_name = "BAAI/bge-small-zh-v1.5"
llm_model_name = "llama3.1:latest" # 确保你已经在Ollama中拉取了这个模型，例如 'ollama pull llama2'

# --- 1. 加载嵌入模型 ---
print(f"正在加载嵌入模型 ({embedding_model_name})...")
try:
    embeddings_model = HuggingFaceBgeEmbeddings(model_name=embedding_model_name)
    print("嵌入模型加载成功。")
except Exception as e:
    print(f"嵌入模型加载失败: {e}")
    print("请检查模型名称是否正确，并确保网络连接正常以便下载模型（如果尚未下载）。")
    exit()

# --- 2. 加载 FAISS 向量数据库 ---
print(f"正在从 {faiss_index_path} 加载 FAISS 向量数据库...")
if not os.path.exists(faiss_index_path):
    print(f"错误: 路径 '{faiss_index_path}' 不存在。请先运行创建数据库的脚本。")
    exit()

try:
    db = FAISS.load_local(faiss_index_path, embeddings_model, allow_dangerous_deserialization=True)
    print("FAISS 向量数据库加载成功。")
except Exception as e:
    print(f"FAISS 向量数据库加载失败: {e}")
    print("请确保 'faiss_index' 文件夹存在且包含有效索引文件，并且嵌入模型与创建时一致。")
    exit()

# --- 3. 初始化语言模型 (LLM) ---
print(f"正在初始化语言模型 ({llm_model_name})...")
try:
    llm = Ollama(model=llm_model_name)
    print("LLM 模型初始化成功。")
except Exception as e:
    print(f"LLM 模型初始化失败，请确保 Ollama 服务正在运行且模型 '{llm_model_name}' 已下载: {e}")
    print("如果你使用的是其他LLM，请替换此部分代码（例如，使用 langchain_openai.ChatOpenAI）。")
    exit()

# --- 4. 创建 RAG 检索问答链 ---
print("正在创建 RAG 检索问答链...")
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever())
print("RAG 链创建成功。")

# --- 5. 提出问题并获取答案 ---
print("\n--- 开始问答 ---")
print("你可以问关于你 Excel 知识库中的问题。")
while True:
    query = input("请输入你的问题 (输入 '退出' 结束): ")
    if query.lower() == '退出':
        break

    print(f"\n你的问题: {query}")
    print("正在检索并生成答案...")

    try:
        result = qa_chain.invoke({"query": query})
        print("\n答案:")
        print(result["result"])
    except Exception as e:
        print(f"在生成答案时发生错误: {e}")
        print("请检查LLM服务是否正常，或尝试简化问题。")

    print("-" * 30)

print("程序结束。")