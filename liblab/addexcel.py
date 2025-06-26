import pandas as pd
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document # 用于封装文档

def import_excel_to_faiss(excel_path, text_column, faiss_index_path="faiss_index"):
    """
    将 Excel 文件中的指定文本列内容导入到 FAISS 向量数据库。

    Args:
        excel_path (str): Excel 文件的路径。
        text_column (str): 包含要向量化的文本的列名。
        faiss_index_path (str): FAISS 索引保存和加载的路径。
    """
    try:
        # 1. 读取 Excel 文件
        print(f"正在读取 Excel 文件: {excel_path}...")
        df = pd.read_excel(excel_path)
        print("Excel 文件读取成功。")

        # 检查指定的文本列是否存在
        if text_column not in df.columns:
            raise ValueError(f"Excel 文件中未找到指定的文本列: '{text_column}'")

        # 提取文本内容，并过滤掉空值
        texts = df[text_column].dropna().tolist()

        if not texts:
            print("Excel 文件中指定列没有可用的文本内容，无法创建向量数据库。")
            return

        # 将文本转换为 Document 对象列表（LangChain 兼容格式）
        # 你也可以根据需要添加元数据，例如来自其他列的信息
        documents = [Document(page_content=text) for text in texts]
        print(f"已从 Excel 中提取 {len(documents)} 条文本记录。")

        # 2. 初始化嵌入模型
        print("正在初始化嵌入模型 (BAAI/bge-small-zh-v1.5)...")
        # 这是一个性能较好的中文嵌入模型
        embeddings_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
        print("嵌入模型初始化成功。")

        # 3. 创建并保存 FAISS 向量数据库
        print("正在创建 FAISS 向量数据库...")
        # from_documents 方法会自动为每个 Document 生成嵌入并构建索引
        db = FAISS.from_documents(documents, embeddings_model)
        db.save_local(faiss_index_path)
        print(f"FAISS 向量数据库已成功创建并保存到: {faiss_index_path}")

        print("\n导入完成！你可以加载此索引进行检索。")

    except FileNotFoundError:
        print(f"错误: 文件 '{excel_path}' 未找到。请检查路径是否正确。")
    except ValueError as ve:
        print(f"错误: {ve}")
    except Exception as e:
        print(f"发生了一个意外错误: {e}")

# --- 如何使用 ---
if __name__ == "__main__":
    # 示例用法
    excel_file = "knowledge_base.xlsx" # 你的 Excel 文件名
    text_column_name = "Answer"       # 包含你想要向量化的文本的列名

    # --- 首先，确保你的 Excel 文件存在并包含数据 ---
    # 如果没有，你可以创建一个简单的 Excel 文件来测试
    # 比如手动创建一个 knowledge_base.xlsx，或者用 pandas 临时创建一个
    try:
        pd.DataFrame({
            "ID": [1, 2, 3],
            "Question": ["什么是RAG？", "Python是什么？", "大语言模型的工作原理"],
            "Answer": ["RAG（检索增强生成）是一种结合了信息检索和文本生成的技术。",
                       "Python是一种广泛使用的高级编程语言，以其简洁明了的语法而闻名。",
                       "大语言模型（LLM）通过在海量文本数据上学习复杂的语言模式和统计关系来生成人类般的文本，能够执行翻译、摘要和问答等任务。"]
        }).to_excel(excel_file, index=False)
        print(f"已创建示例 Excel 文件: {excel_file}")
    except Exception as e:
        print(f"创建示例 Excel 文件失败: {e}")

    # 运行导入函数
    import_excel_to_faiss(excel_file, text_column_name)

    # --- 演示如何加载和使用数据库进行检索 ---
    print("\n--- 演示检索 ---")
    try:
        # 加载之前保存的 FAISS 索引
        embeddings_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
        loaded_db = FAISS.load_local("faiss_index", embeddings_model, allow_dangerous_deserialization=True)
        print("FAISS 索引加载成功。")

        query = "RAG是什么意思？"
        print(f"查询: {query}")
        # 执行相似性搜索
        docs_found = loaded_db.similarity_search(query, k=2) # 检索最相似的2个文档

        print("\n检索到的相关文档:")
        for i, doc in enumerate(docs_found):
            print(f"--- 文档 {i+1} ---")
            print(f"内容: {doc.page_content}")
            # 如果你在 Document 对象中添加了元数据，这里也可以访问 doc.metadata
            print("-" * 15)

    except Exception as e:
        print(f"检索演示失败: {e}")
        print("请确保 FAISS 索引已成功创建并保存。")