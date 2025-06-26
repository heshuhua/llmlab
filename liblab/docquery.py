from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_core.retrievers import BaseRetriever # Import BaseRetriever
from langchain_core.documents import Document # Ensure Document is imported from core if it's used directly
import os
import datetime
from typing import List # Import List for type hinting

# --- 配置 ---
faiss_index_path = "law_firm_word_faiss_index" # 与构建时使用的路径一致
embedding_model_name = "BAAI/bge-small-zh-v1.5"
llm_model_name = "llama3.1:latest" # 确保 Ollama 中已下载此模型

# --- 1. 加载嵌入模型 ---
print(f"正在加载嵌入模型 ({embedding_model_name})...")
try:
    embeddings_model = HuggingFaceBgeEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={'local_files_only': True}
    )
    print("嵌入模型加载成功。")
except Exception as e:
    print(f"嵌入模型加载失败: {e}")
    exit()

# --- 2. 加载 FAISS 向量数据库 ---
print(f"正在从 {faiss_index_path} 加载 FAISS 向量数据库...")
if not os.path.exists(faiss_index_path):
    print(f"错误: 路径 '{faiss_index_path}' 不存在。请先运行 build_word_kb.py。")
    exit()

try:
    db = FAISS.load_local(faiss_index_path, embeddings_model, allow_dangerous_deserialization=True)
    print("法律事务所 Word 知识库加载成功。")
except Exception as e:
    print(f"知识库加载失败: {e}")
    exit()

# --- 3. 初始化 LLM ---
print(f"正在初始化语言模型 ({llm_model_name})...")
try:
    llm = Ollama(model=llm_model_name)
    print("LLM 模型初始化成功。")
except Exception as e:
    print(f"LLM 模型初始化失败，请确保 Ollama 服务正在运行且模型 '{llm_model_name}' 已下载: {e}")
    exit()

# --- 4. 修改 CustomRetriever 以继承自 BaseRetriever ---
from typing import List, Optional # Import Optional

# ... (rest of your imports)

# --- 4. 修改 CustomRetriever 以继承自 BaseRetriever ---
class CustomFilteredRetriever(BaseRetriever): # Inherit from BaseRetriever
    db: FAISS
    # Change these lines to use Optional
    doc_type_filter: Optional[str] = None
    min_date_filter: Optional[datetime.date] = None

    # Implement the abstract method _get_relevant_documents
    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        # ... (your existing filtering logic) ...
        docs = self.db.similarity_search(query, k=10) # Retrieve more documents for filtering

        filtered_docs = []
        for doc in docs:
            keep_doc = True
            # Check document type filter
            if self.doc_type_filter: # This check is now correct as doc_type_filter could be None
                if doc.metadata.get('doc_type') != self.doc_type_filter:
                    keep_doc = False
            # Check date filter
            if self.min_date_filter and keep_doc: # This check is also correct
                last_updated_str = doc.metadata.get('last_updated')
                if last_updated_str:
                    try:
                        last_updated_date = datetime.datetime.strptime(last_updated_str, '%Y-%m-%d').date()
                        if last_updated_date < self.min_date_filter:
                            keep_doc = False
                    except ValueError:
                        pass # Date format error, skip this filter

            if keep_doc:
                filtered_docs.append(doc)

        return filtered_docs[:3] # Return top 3 after filtering

    # Implement the abstract method _aget_relevant_documents for async (optional, but good practice)
    async def _aget_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        return self._get_relevant_documents(query, **kwargs)

# ... (rest of your script) ...
# --- 5. 问答环节 ---
print("\n--- 法律事务所 RAG 问答 ---")
print("你可以问关于文档内容的问题，并选择是否添加过滤条件。")

while True:
    query = input("\n请输入你的问题 (输入 '退出' 结束): ")
    if query.lower() == '退出':
        break

    filter_doc_type = input("你想限定文档类型吗？(例如: 合同模板, 法律意见书, 内部规章, 或留空): ").strip()
    filter_date_str = input("你想只看某个日期之后更新的文档吗？(例如: 2024-03-01, 或留空): ").strip()

    min_date = None
    if filter_date_str:
        try:
            min_date = datetime.datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        except ValueError:
            print("日期格式无效，将不使用日期过滤。")

    print(f"\n你的问题: {query}")
    print(f"筛选条件 - 文档类型: {filter_doc_type if filter_doc_type else '无'}, 最早更新日期: {min_date if min_date else '无'}")
    print("正在检索并生成答案...")

    # 根据用户输入的过滤条件创建检索器实例
    # Now instantiate CustomFilteredRetriever directly
    my_retriever = CustomFilteredRetriever(
        db=db, # Pass the FAISS database instance
        doc_type_filter=filter_doc_type if filter_doc_type else None,
        min_date_filter=min_date
    )

    # 创建并调用 RAG 链
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=my_retriever)
    try:
        result = qa_chain.invoke({"query": query})
        print("\n答案:")
        print(result["result"])

        # 额外打印检索到的文档的元数据，以证明过滤生效
        print("\n--- 检索到的原始文档信息 (用于调试) ---")
        # Call the retriever directly to see the filtered docs
        retrieved_docs_for_debug = my_retriever.get_relevant_documents(query)
        if retrieved_docs_for_debug:
            for i, doc in enumerate(retrieved_docs_for_debug):
                print(f"文档 {i+1} (来自知识库):")
                print(f"  来源: {doc.metadata.get('source', 'N/A')}")
                print(f"  标题: {doc.metadata.get('title', 'N/A')}")
                print(f"  类型: {doc.metadata.get('doc_type', 'N/A')}")
                print(f"  更新: {doc.metadata.get('last_updated', 'N/A')}")
                print(f"  内容: {doc.page_content[:100]}...")
                print("-" * 15)
        else:
            print("  没有文档符合筛选条件被检索到。")

    except Exception as e:
        print(f"在生成答案时发生错误: {e}")
        print("请检查你的LLM服务是否正常，或尝试不同的问题。")

    print("\n" + "=" * 50)

print("程序结束。")