from datasets import load_dataset

# 加载本地数据集
data_files = {"train": "tea_data.jsonl"}
dataset = load_dataset("json", data_files=data_files)

# 可以查看数据集的一些信息
print(dataset)
print(dataset["train"][0])