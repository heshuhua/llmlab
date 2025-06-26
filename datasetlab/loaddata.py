from datasets import load_dataset

# 加载 cmrc2018 数据集
# split 参数用于指定加载哪个子集（train, validation, test）
# 如果不指定 split，load_dataset 可能会返回一个 DatasetDict 对象
# 包含所有的分割。
cmrc2018_train_dataset = load_dataset("cmrc2018", split="train")
cmrc2018_validation_dataset = load_dataset("cmrc2018", split="validation")
cmrc2018_test_dataset = load_dataset("cmrc2018", split="test")

# 你也可以一次性加载所有分割
# cmrc2018_datasets = load_dataset("cmrc2018")
# print(cmrc2018_datasets)
# print(cmrc2018_datasets['train'])

print("训练集信息：")
print(cmrc2018_train_dataset)
print("\n训练集前5条数据：")
print(cmrc2018_train_dataset[:5])

print("\n验证集信息：")
print(cmrc2018_validation_dataset)
print("\n测试集信息：")
print(cmrc2018_test_dataset)