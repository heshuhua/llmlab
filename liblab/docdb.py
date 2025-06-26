from langchain_community.document_loaders import Docx2txtLoader # 用于加载.docx文件
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import os

# --- 配置 ---
word_docs_dir = "word_kb"
faiss_index_path = "law_firm_word_faiss_index"
embedding_model_name = "BAAI/bge-small-zh-v1.5"

def build_word_knowledge_base():
    documents = []
    
    # 1. 加载 Word 文档
    print(f"正在加载 Word 文档从目录: {word_docs_dir}...")
    if not os.path.exists(word_docs_dir):
        print(f"错误: 目录 '{word_docs_dir}' 不存在。请先运行 create_sample_word_docs.py。")
        return None

    for root, _, files in os.walk(word_docs_dir):
        for file in files:
            if file.endswith(".docx"):
                filepath = os.path.join(root, file)
                loader = Docx2txtLoader(filepath)
                # 每个Word文档可能包含多个页面的内容，load()会返回一个列表
                loaded_docs = loader.load()
                
                # 为每个加载的文档添加元数据
                for doc in loaded_docs:
                    # 从文件名中提取文档类型和标题作为元数据
                    file_parts = os.path.splitext(file)[0].split('-')
                    doc_type = file_parts[0] if len(file_parts) > 1 else "未知类型"
                    doc_title = file.replace(".docx", "") # 完整文件名作为标题
                    
                    # 可以在这里添加更多从文档内容或文件名解析出的元数据
                    doc.metadata = {
                        "source": filepath,
                        "doc_type": doc_type.strip(), # 比如 "劳动合同", "法律意见书"
                        "title": doc_title.strip(),
                        "last_updated": datetime.date.today().strftime('%Y-%m-%d') # 示例日期，实际可以从文件属性获取
                    }
                    documents.append(doc)
    
    if not documents:
        print("未找到任何 Word 文档或文档内容为空，无法创建知识库。")
        return None

    print(f"已加载 {len(documents)} 个 Word 文档。")

    # 2. 文本分割
    print("正在分割文档...")
    # 使用递归字符文本分割器，可以更好地处理长文档的结构
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 每个文本块的最大长度
        chunk_overlap=100, # 块之间的重叠，有助于保留上下文
        length_function=len,
        add_start_index=True, # 添加 chunk 在原始文档中的起始位置
    )
    docs = text_splitter.split_documents(documents)
    print(f"文档已分割成 {len(docs)} 个文本块。")

    # 3. 创建嵌入模型
    print("正在初始化嵌入模型...")
    embeddings_model = HuggingFaceBgeEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={'local_files_only': True} # 假设模型已下载
    )
    print("嵌入模型初始化成功。")

    # 4. 创建并保存 FAISS 向量数据库
    print("正在创建 FAISS 向量数据库...")
    db = FAISS.from_documents(docs, embeddings_model)
    db.save_local(faiss_index_path)
    print(f"FAISS 向量数据库已成功创建并保存到: {faiss_index_path}")
    return db

if __name__ == "__main__":
    import datetime # 确保datetime已导入

    # 确保创建了示例 Word 文档
    # 第一次运行前请先运行 create_sample_word_docs.py
    # python create_sample_word_docs.py

    build_word_knowledge_base()