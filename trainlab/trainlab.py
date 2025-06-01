from datasets import load_dataset

from transformers import AutoTokenizer

# 加载与模型对应的 tokenizer
model_id = "meta-llama/Meta-Llama-3-8B"  # 或者你使用的 llama3 模型名
tokenizer = AutoTokenizer.from_pretrained(model_id)


dataset = load_dataset("cmrc2018")
train_data = dataset['train']

def format_qa(example):
    prompt = f"问：{example['question']}\n上下文：{example['context']}\n答："
    answer = example['answers']['text'][0] if example['answers']['text'] else "无答案"
    return {
        "input_ids": tokenizer(prompt, truncation=True)["input_ids"],
        "labels": tokenizer(answer, truncation=True)["input_ids"]
    }

train_data = train_data.map(format_qa)
