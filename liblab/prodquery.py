from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
import os
import datetime

# --- 配置 ---
faiss_index_path = "it_support_faiss_index"
embedding_model_name = "BAAI/bge-small-zh-v1.5"
llm_model_name = "llama3.1:latest"

# --- 1. 加载嵌入模型 ---
embeddings_model = HuggingFaceBgeEmbeddings(model_name=embedding_model_name,model_kwargs={'local_files_only': True})

# --- 2. 加载 FAISS 向量数据库 ---
if not os.path.exists(faiss_index_path):
    print(f"错误: 路径 '{faiss_index_path}' 不存在。请先运行创建数据库的脚本。")
    exit()

try:
    db = FAISS.load_local(faiss_index_path, embeddings_model, allow_dangerous_deserialization=True)
    print("IT 支持知识库加载成功。")
except Exception as e:
    print(f"知识库加载失败: {e}")
    exit()

# --- 3. 初始化 LLM ---
try:
    llm = Ollama(model=llm_model_name)
except Exception as e:
    print(f"LLM 初始化失败: {e}")
    exit()

# --- 4. 创建 RAG 链 ---
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever())

# --- 5. 问答环节 ---
print("\n--- IT 支持问答 ---")
print("你可以尝试提出问题，并选择是否添加过滤条件。")

while True:
    query = input("\n请输入你的问题 (输入 '退出' 结束): ")
    if query.lower() == '退出':
        break

    filter_category = input("你想限定产品类别吗？(例如: 软件, 硬件, 网络, 或留空): ").strip()
    filter_date_str = input("你想只看最近更新的答案吗？(例如: 2024-05-01, 或留空): ").strip()

    min_date = None
    if filter_date_str:
        try:
            min_date = datetime.datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        except ValueError:
            print("日期格式无效，将不使用日期过滤。")

    print(f"\n你的问题: {query}")
    print(f"筛选条件 - 类别: {filter_category if filter_category else '无'}, 最早更新日期: {min_date if min_date else '无'}")
    print("正在检索并生成答案...")

    try:
        result = qa_chain.invoke({"query": query})
        print("\n答案:")
        print(result["result"])

        # 额外打印检索到的文档的元数据，并进行过滤
        print("\n--- 检索到的原始文档信息 (用于调试) ---")
        retrieved_docs = db.similarity_search(query, k=10) # 检索更多文档
        filtered_docs = []
        for doc in retrieved_docs:
            keep_doc = True
            if filter_category and doc.metadata.get('category') != filter_category:
                keep_doc = False
            if min_date:
                last_updated_str = doc.metadata.get('last_updated')
                if last_updated_str:
                    try:
                        last_updated_date = datetime.datetime.strptime(last_updated_str, '%Y-%m-%d').date()
                        if last_updated_date < min_date:
                            keep_doc = False
                    except ValueError:
                        pass
            if keep_doc:
                filtered_docs.append(doc)

        if filtered_docs:
            for i, doc in enumerate(filtered_docs[:3]):  # Show top 3 after filtering
                print(f"文档 {i+1} (来自知识库):")
                print(f"  内容: {doc.page_content[:50]}...")
                print(f"  元数据: {doc.metadata}")
                print("-" * 10)
        else:
            print("  没有文档符合筛选条件被检索到。")

    except Exception as e:
        print(f"在生成答案时发生错误: {e}")
        print("请检查你的LLM服务是否正常，或尝试不同的问题。")

    print("\n" + "=" * 50)

print("程序结束。")