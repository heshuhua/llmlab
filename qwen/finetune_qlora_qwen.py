import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    BitsAndBytesConfig, TrainingArguments,
    Trainer, DataCollatorWithPadding
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from sklearn.metrics import accuracy_score

# 🧠 标签映射
label2id = {"天气": 0, "健康": 1, "旅游": 2}
id2label = {v: k for k, v in label2id.items()}

# ✅ 1. 加载数据集（train.jsonl / test.jsonl）
def preprocess(example):
    text = example["text"]
    label = label2id[example["label"]]
    return {"text": text, "label": label}

dataset = load_dataset("json", data_files={"train": "train.jsonl", "test": "test.jsonl"})
dataset = dataset.map(preprocess)

# ✅ 2. 加载 tokenizer & 模型（Qwen1.5-0.5B, 4-bit）
model_id = "Qwen/Qwen1.5-0.5B"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
)

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # 避免 padding 报错

model = AutoModelForCausalLM.from_pretrained(model_id,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# ✅ 3. QLoRA 配置
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["c_attn", "q_proj", "v_proj"],  # 根据模型架构调整
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

# ✅ 4. 数据编码
def tokenize(example):
    prompt = f"请判断这个问题的类型：{example['text']}。\n选项：天气、健康、旅游。"
    label = label2id[example["label"]]
    inputs = tokenizer(prompt, truncation=True, padding="max_length", max_length=128)
    inputs["labels"] = label
    return inputs

tokenized_dataset = dataset.map(tokenize)

# ✅ 5. 训练配置
training_args = TrainingArguments(
    output_dir="./qwen_qlora_clf",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=5,
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-4,
    save_total_limit=1,
    remove_unused_columns=False,
    fp16=torch.cuda.is_available(),
)

# ✅ 6. 指标评估
def compute_metrics(eval_pred):
    preds = torch.argmax(torch.tensor(eval_pred.predictions), dim=-1)
    labels = torch.tensor(eval_pred.label_ids)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

# ✅ 7. 训练启动
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics
)

trainer.train()
