import pandas as pd
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import os

def create_it_support_kb(excel_path, faiss_index_path="risk_support_faiss_index"):
    """
    从 Excel 创建 风险评估 支持知识库的 FAISS 向量数据库，并包含元数据。
    """
    try:
        print(f"正在读取 需求风险评估表 支持知识库 Excel 文件: {excel_path}...")
        df = pd.read_excel(excel_path)
        print("Excel 文件读取成功。")

        documents = []
        # 遍历 DataFrame 的每一行
        for index, row in df.iterrows():
            # 将 '答案' 列作为 page_content
            page_content = str(row['需求内容概要简述']) # 确保是字符串类型

            integrated_content = (
              f"需求内容概要简述: {row['需求内容概要简述']}.  计划上线时间: {row['计划上线时间']}."
            )

            # 将其他列作为元数据
            metadata = {
                "id": row['用户需求名称'],
                "question": str(row['用户需求名称']),
                "category": str(row['归属项目经理']),
                "last_updated": str(row['计划上线时间']) # 保持为字符串或转换为日期对象
            }
            documents.append(Document(page_content=integrated_content, metadata=metadata))

        if not documents:
            print("Excel 文件中没有可用的文档内容，无法创建向量数据库。")
            return

        print(f"已从 Excel 中提取 {len(documents)} 条文档记录，包含元数据。")

        # 初始化嵌入模型
        embeddings_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

        # 创建并保存 FAISS 向量数据库
        print("正在创建 FAISS 向量数据库...")
        db = FAISS.from_documents(documents, embeddings_model)
        db.save_local(faiss_index_path)
        print(f"FAISS 向量数据库已成功创建并保存到: {faiss_index_path}")

    except FileNotFoundError:
        print(f"错误: 文件 '{excel_path}' 未找到。请检查路径是否正确。")
    except KeyError as ke:
        print(f"错误: Excel 文件中缺少列。请确保包含 'ID', '问题', '答案', '项目经理', '投产时间' 列。缺失列: {ke}")
    except Exception as e:
        print(f"发生了一个意外错误: {e}")

if __name__ == "__main__":
    excel_file = "req2025.xlsx"
    # 创建一个示例 Excel 文件（如果不存在）
    if not os.path.exists(excel_file):
        sample_data = {
            "ID": [1, 2, 3, 4, 5, 6],
            "问题": [
                "如何连接公司 Wi-Fi？",
                "Outlook 无法发送邮件怎么办？",
                "我的笔记本电脑无法开机。",
                "如何申请新的鼠标或键盘？",
                "VPN 连接不上如何排查？",
                "SharePoint 共享文件权限问题。"
            ],
            "答案": [
                "请确保您已选择“CorpNet”网络，并输入您的员工ID和密码。首次连接可能需要接受安全证书。",
                "检查您的网络连接。尝试重启 Outlook 或您的电脑。如果问题仍然存在，请联系IT服务台。",
                "检查电源适配器是否连接好。尝试按住电源按钮10秒强制关机，然后重新启动。",
                "请在内部IT门户提交配件申请表。选择您需要的设备型号并提交。",
                "请确认您的VPN客户端是最新版本。尝试更换网络环境。如果仍然无法连接，可能是您的账户被锁定，请联系IT服务台。",
                "确保您对该文件夹具有“编辑”或“完全控制”权限。如果权限不足，请联系文件所有者或IT管理员。"
            ],
            "产品类别": [
                "网络", "软件", "硬件", "硬件", "网络", "软件"
            ],
            "最后更新": [
                "2024-05-10", "2024-06-01", "2024-04-20", "2024-05-15", "2024-06-10", "2024-06-05"
            ]
        }
        pd.DataFrame(sample_data).to_excel(excel_file, index=False)
        print(f"已创建示例 IT 支持知识库 Excel 文件: {excel_file}")

    create_it_support_kb(excel_file)