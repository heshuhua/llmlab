import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from peft import LoraConfig, get_peft_model, TaskType
from sklearn.metrics import accuracy_score

# ✅ 屏蔽 wandb
os.environ["WANDB_DISABLED"] = "true"

# ✅ 标签映射
label2id = {"天气": 0, "健康": 1, "旅游": 2}
id2label = {v: k for k, v in label2id.items()}

# ✅ 加载 jsonl 数据集并预处理
def preprocess(example):
    return {"text": example["text"], "label": label2id[example["label"]]}

dataset = load_dataset("json", data_files={"train": "train.jsonl", "test": "test.jsonl"})
dataset = dataset.map(preprocess)

# ✅ 加载 tokenizer 和 base 模型
model_id = "Qwen/Qwen1.5-0.5B"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    device_map="auto"
)
model.config.use_cache = False  # 防止 LoRA 报错

# ✅ LoRA 配置
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["c_attn", "q_proj", "v_proj"],  # Qwen架构
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, lora_config)

# ✅ 构造 prompt 并 tokenize
def tokenize(example):
    prompt = f"请判断这个问题的类型：{example['text']}。\n选项：天气、健康、旅游。"
    encoded = tokenizer(
        prompt,
        padding="max_length",
        truncation=True,
        max_length=128
    )
    encoded["labels"] = label2id[example["label"]]
    return encoded

tokenized_dataset = dataset.map(tokenize)

# ✅ 训练配置
training_args = TrainingArguments(
    output_dir="./qwen_lora_clf",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=5,
    logging_steps=10,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    save_total_limit=1,
    learning_rate=2e-4,
    remove_unused_columns=False,
    report_to=[]  # 不使用 wandb
)

# ✅ 评估函数
def compute_metrics(eval_pred):
    logits = torch.tensor(eval_pred.predictions)
    preds = torch.argmax(logits, dim=-1)
    labels = torch.tensor(eval_pred.label_ids)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

# ✅ 启动 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics
)

# ✅ 开始训练
trainer.train()

# ✅ 保存模型
model.save_pretrained("./qwen_lora_clf/lora_model")
tokenizer.save_pretrained("./qwen_lora_clf/lora_model")
