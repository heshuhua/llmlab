from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
import torch

# === 模型 ID（你本地已下载） ===
model_id = "meta-llama/Meta-Llama-3-8B"

# === 加载 tokenizer，并指定 pad_token ===
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token  # ✅ 修复 padding 报错

# === 加载模型 ===
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map={"": "cpu"},  # Mac 上用 CPU 跑
    torch_dtype=torch.float16
)

# === 通知模型词表已变动 ===
model.resize_token_embeddings(len(tokenizer))

# === 应用 LoRA 微调配置（节省内存）===
peft_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, peft_config)

# === 加载中文问答数据集（CMRC 2018）===
dataset = load_dataset("cmrc2018")
train_data = dataset["train"].select(range(100))

# === 格式化为 LLM 输入格式 ===
def format_qa(example):
    prompt = f"问：{example['question']}\n上下文：{example['context']}\n答："
    answer = example['answers']['text'][0] if example['answers']['text'] else "无答案"
    full_text = prompt + answer

    tokenized = tokenizer(
        full_text,
        padding="max_length",
        truncation=True,
        max_length=512
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

train_data = train_data.map(format_qa, remove_columns=train_data.column_names)

# === 训练参数 ===
training_args = TrainingArguments(
    output_dir="./lora-llama3-zhqa",
    per_device_train_batch_size=1,
    num_train_epochs=1,
    logging_steps=10,
    save_steps=100,
    save_total_limit=1,
    report_to="none"
)

# === 启动 Trainer ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data
)

# === 开始训练 ===
trainer.train()

# === 手动保存微调后的 LoRA 模型 ===
model.save_pretrained("./lora-llama3-zhqa-debug")
