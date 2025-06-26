import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, PeftModel # 移除 prepare_model_for_kbit_training
from datasets import load_dataset

# --- 第一步：环境准备（与之前相同，确保已安装） ---
# pip install transformers accelerate peft datasets
# 注意：此版本不再需要 bitsandbytes，因为我们禁用了量化和 paged_adamw_8bit

# --- 第二步：加载预训练模型和分词器 (调整前) ---
model_name = "Qwen/Qwen1.5-0.5B"

# 加载分词器
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 为 Qwen 模型设置 pad_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right" # Qwen 推荐 padding_side 是 right

# 原始模型推理函数
def generate_response(prompt, model, tokenizer):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device) # model.device 会是 "cpu"

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=100,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        pad_token_id=tokenizer.pad_token_id
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

# 示例问题：
prompts_before = [
    "请介绍一下珍珠奶茶的历史。",
    "制作一杯好喝的绿茶拿铁需要哪些步骤？",
    "红茶和绿茶有什么区别？",
    "推荐几款适合夏天的清爽茶饮。",
    "茶叶的种类有哪些？"
]

print("===== 调整前模型加载及输出示例 (CPU 运行) =====")
# 在微调前加载并测试原始模型
# !!! 调整：明确加载到 CPU，并使用 float32 精度 !!!
base_model_for_initial_test = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, device_map="cpu")
base_model_for_initial_test.eval()

for i, prompt in enumerate(prompts_before):
    print(f"\n--- 问题 {i+1}: {prompt} ---")
    response_before = generate_response(prompt, base_model_for_initial_test, tokenizer)
    print(f"模型回答: {response_before}")

# 释放内存
del base_model_for_initial_test
# 注意：在 CPU 环境下，torch.cuda.empty_cache() 是无效的，可以移除或不执行

# --- 第三步：准备微调数据集 (与之前相同) ---
# 确保 tea_data.jsonl 文件存在且格式正确
# 例如：
# {"messages": [{"role": "system", "content": "您是一位专业的茶饮顾问。"}, {"role": "user", "content": "珍珠奶茶是怎么发明的？"}, {"role": "assistant", "content": "珍珠奶茶起源于台湾，..."}]}

data_files = {"train": "tea_data.jsonl"}
dataset = load_dataset("json", data_files=data_files)

print(f"\n===== 数据集加载完成：{dataset} =====")
print(f"数据集示例：{dataset['train'][0]}")

# --- 第四步：配置微调参数及模型加载 (重点调整部分) ---

# 加载用于训练的模型
# !!! 调整：明确加载到 CPU，并使用 float32 精度 !!!
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32, # CPU 运行通常使用 float32
    device_map="cpu" # 明确指定在 CPU 上运行
)

# !!! 调整：在 CPU 模式下不需要 prepare_model_for_kbit_training 和 BitsAndBytesConfig !!!
# !!! 但是 enable_input_require_grads() 对于 LoRA 依然重要，即使是 CPU ！！！
model.enable_input_require_grads()

# LoRA 配置
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none",
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

# 应用 LoRA 配置到模型
model = get_peft_model(model, lora_config)
print("\n===== 模型应用 LoRA 配置完成 =====")
model.print_trainable_parameters() # 打印可训练参数数量，应该非常小

# 数据预处理函数
def preprocess_function(examples):
    processed_examples = []
    for messages in examples["messages"]:
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        processed_examples.append(text)
    return tokenizer(processed_examples, truncation=True, max_length=512)

tokenized_dataset = dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=["messages"]
)

# 数据整理器
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# 训练参数
training_args = TrainingArguments(
    output_dir="./qwen_finetuned_tea",
    num_train_epochs=3,
    per_device_train_batch_size=1, # !!! 调整：CPU 批次大小通常需要更小，因为内存受限且速度慢 !!!
    gradient_accumulation_steps=8, # !!! 调整：增加梯度累积以模拟更大的批次大小 !!!
    gradient_checkpointing=True, # 启用梯度检查点，节省内存 (即使 CPU 也有用)
    optim="adamw_torch", # !!! 调整：CPU 兼容的优化器 !!!
    learning_rate=2e-4,
    fp16=False, # !!! 关键调整：禁用 FP16 !!!
    save_strategy="epoch",
    logging_steps=10,
    report_to="none",
)

# 初始化 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# --- 第五步：开始微调 ---
print("\n===== 开始微调模型 (CPU 模式) =====")
trainer.train()
print("\n===== 微调完成 =====")

# 保存微调后的 LoRA 适配器
trainer.save_model("./qwen_finetuned_tea")
print(f"微调后的 LoRA 适配器已保存到：{training_args.output_dir}")

# --- 第六步：加载微调后的模型并进行推理 (调整后) ---

# 清理内存
del model
del trainer
# torch.cuda.empty_cache() 在 CPU 环境下无效

print("\n===== 加载微调后的模型进行对比 (CPU 模式) =====")
# 重新加载基础模型 (不带 LoRA)
base_model_for_inference = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, device_map="cpu")

# 加载微调后的 LoRA 适配器
peft_model_id = "./qwen_finetuned_tea"
model_after_finetune = PeftModel.from_pretrained(base_model_for_inference, peft_model_id)

# 将 LoRA 权重合并到基础模型中
model_after_finetune = model_after_finetune.merge_and_unload()
model_after_finetune.eval()

print("微调后模型加载并合并完成。")

# 测试调整后的模型
print("\n===== 调整后模型输出示例 (与调整前相同的问题) =====")
for i, prompt in enumerate(prompts_before):
    print(f"\n--- 问题 {i+1}: {prompt} ---")
    response_after = generate_response(prompt, model_after_finetune, tokenizer)
    print(f"模型回答: {response_after}")

# 尝试一些新的问题
prompts_after = [
    "冰美式和冰拿铁有什么区别？",
    "什么茶适合在饭后饮用？",
    "介绍一下中国六大茶类。",
    "如何辨别茶叶的品质好坏？",
    "推荐一款适合作为下午茶的茶点搭配。",
]

print("\n===== 调整后模型新问题输出示例 =====")
for i, prompt in enumerate(prompts_after):
    print(f"\n--- 新问题 {i+1}: {prompt} ---")
    response_new = generate_response(prompt, model_after_finetune, tokenizer)
    print(f"模型回答: {response_new}")