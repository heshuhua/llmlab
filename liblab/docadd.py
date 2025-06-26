import pandas as pd

# 读取 Excel
df = pd.read_excel("req2025.xlsx", header=1)

# 选择我们关心的列
df = df[["需求负责人-需求发布时填写", "需求负责人-需求发布时填写.1", "组长-代码评审时填写.20"]]
df.columns = ["需求名称", "需求简述", "上线日期"]

# 拼接成知识库文本
docs = []
for idx, row in df.iterrows():
    content = f"{row['需求名称']}：{row['需求简述']}。上线时间为：{row['上线日期']}"
    docs.append(content)

