import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import load_dataset
import json

# --- 配置：CPU 强制运行，禁用 FP16 和量化 ---
# 此配置适用于没有CUDA GPU的环境。
# 如果您有NVIDIA GPU且已正确配置CUDA，并希望利用GPU加速（如FP16、bitsandbytes），
# 请参考之前“版本 B”的指导，并启用相关设置。
device = "cpu"
torch_dtype = torch.float32 # 在CPU上通常使用float32
use_fp16 = False # 禁用FP16
optimizer_name = "adamw_torch" # CPU兼容的优化器

# --- 模型加载和分词器 ---
model_name = "Qwen/Qwen1.5-0.5B" # 确保模型已下载或可自动下载

tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right" # Qwen模型推荐右侧填充

# --- 辅助函数：模型生成响应 (用于分类任务) ---
def generate_response_for_classification(prompt_text, model, tokenizer, max_new_tokens=20):
    messages = [
        {"role": "system", "content": "你是一位专业的茶饮分类助手。请根据描述准确分类茶饮类型。你的回答只包含茶饮类型，不包含其他内容。"},
        {"role": "user", "content": prompt_text}
    ]
    # 使用apply_chat_template将消息列表转换为模型期望的格式
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    # 将输入移动到模型所在的设备 (CPU)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=max_new_tokens, # 预期分类结果较短，所以减少生成长度
        do_sample=True,
        temperature=0.1, # 降低温度，使分类结果更确定
        top_k=1, # 降低top_k和top_p，进一步提高确定性，避免生成无关内容
        top_p=1.0,
        pad_token_id=tokenizer.pad_token_id
    )
    # 解码时跳过输入部分
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    # 对生成结果进行清理，移除可能的空白符
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return response

# --- 加载中文测试数据 ---
test_data_path = "tea_classification_test_zh.jsonl"
with open(test_data_path, "r", encoding="utf-8") as f:
    test_samples = [json.loads(line) for line in f]

print(f"加载了 {len(test_samples)} 条中文测试数据。")

# --- 评估函数 ---
def evaluate_classification(model, tokenizer, test_samples, phase="调整前"):
    correct_predictions = 0
    total_predictions = len(test_samples)

    print(f"\n===== {phase} 模型中文分类结果 =====")
    for i, sample in enumerate(test_samples):
        prompt_text = sample["instruction"]
        true_label = sample["output"].strip().lower() # 确保真实标签被清理并小写

        # 调用模型进行分类
        predicted_label_raw = generate_response_for_classification(prompt_text, model, tokenizer)
        predicted_label = predicted_label_raw.strip().lower() # 清理并小写预测标签

        # 使用精确匹配来判断类别是否正确
        is_correct = (predicted_label == true_label)

        status = "✔ 正确" if is_correct else "✗ 错误"

        print(f"--- 样本 {i+1} ---")
        print(f"描述: {prompt_text}")
        print(f"真实类别: {true_label}")
        print(f"预测类别: {predicted_label_raw} (清理后: {predicted_label}) ({status})") # 显示原始和清理后的预测
        print("-" * 20)
        
        if is_correct:
            correct_predictions += 1
    
    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"\n{phase} 模型中文分类准确率: {accuracy:.2f}% ({correct_predictions}/{total_predictions})")
    return accuracy


# # --- 评估函数 ---
# def evaluate_classification(model, tokenizer, test_samples, phase="调整前"):
#     correct_predictions = 0
#     total_predictions = len(test_samples)

#     print(f"\n===== {phase} 模型中文分类结果 =====")
#     for i, sample in enumerate(test_samples):
#         prompt_text = sample["instruction"]
#         true_label = sample["output"]

#         # 调用模型进行分类
#         predicted_label = generate_response_for_classification(prompt_text, model, tokenizer)

#         # 简单的字符串包含匹配来判断是否正确，考虑LLM可能生成冗余内容
#         # 确保比较时都转为小写或统一格式，以避免大小写或全半角问题
#         is_correct = true_label.lower() in predicted_label.lower()

#         status = "✔ 正确" if is_correct else "✗ 错误"

#         print(f"--- 样本 {i+1} ---")
#         print(f"描述: {prompt_text}")
#         print(f"真实类别: {true_label}")
#         print(f"预测类别: {predicted_label} ({status})")
#         print("-" * 20)
    
#     accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
#     print(f"\n{phase} 模型中文分类准确率: {accuracy:.2f}% ({correct_predictions}/{total_predictions})")
#     return accuracy

# --- 阶段 1：微调前模型评估 ---
print("\n===== 正在加载原始模型进行微调前中文评估 (CPU 模式) =====")
base_model_for_initial_test = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch_dtype,
    device_map=device
)
base_model_for_initial_test.eval()

# 运行微调前评估
evaluate_classification(base_model_for_initial_test, tokenizer, test_samples, phase="调整前")

# 释放内存
del base_model_for_initial_test


# --- 阶段 2：准备微调数据集 ---
train_data_path = "tea_classification_train_zh.jsonl"
data_files = {"train": train_data_path}
dataset = load_dataset("json", data_files=data_files)

print(f"\n===== 中文训练数据集加载完成：{dataset} =====")
print(f"训练数据集示例：{dataset['train'][0]}")

# --- 阶段 3：配置微调模型 ---
print("\n===== 正在加载模型并应用 LoRA 配置进行微调 (CPU 模式) =====")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch_dtype,
    device_map=device
)

# !!! 关键步骤：为LoRA确保输入需要梯度 !!!
model.enable_input_require_grads()

# LoRA 配置
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none",
    lora_dropout=0.05,
    task_type="CAUSAL_LM", # 仍然是因果语言建模任务
)

# 应用 LoRA 配置到模型
model = get_peft_model(model, lora_config)
print("\n===== 模型应用 LoRA 配置完成 =====")
model.print_trainable_parameters()

# 数据预处理函数：将对话格式转换为模型可训练的token ids
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
    output_dir="./qwen_finetuned_classification_zh",
    num_train_epochs=20, # 增加epochs，因为分类任务需要更强的模式学习
    per_device_train_batch_size=1, # CPU内存限制，批次大小更小
    gradient_accumulation_steps=8, # 增加梯度累积以模拟更大的批次大小 (1 * 8 = 8)
    gradient_checkpointing=True, # 启用梯度检查点，节省内存
    optim=optimizer_name, # 使用CPU兼容的优化器
    learning_rate=2e-4,
    fp16=use_fp16, # 禁用FP16
    save_strategy="epoch",
    logging_steps=10,
    report_to="none",
    save_total_limit=1, # 只保存最后一个检查点
)

# 初始化 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# --- 阶段 4：开始微调 ---
print("\n===== 开始微调模型 (CPU 模式) =====")
trainer.train()
print("\n===== 微调完成 =====")

# 保存微调后的LoRA适配器
trainer.save_model("./qwen_finetuned_classification_zh")
print(f"微调后的LoRA适配器已保存到：{training_args.output_dir}")

# --- 阶段 5：微调后模型评估 ---
print("\n===== 正在加载微调后的模型进行评估 (CPU 模式) =====")
# 清理内存
del model
del trainer

# 重新加载基础模型 (不带LoRA)
base_model_for_inference = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch_dtype,
    device_map=device
)

# 加载微调后的LoRA适配器
peft_model_id = "./qwen_finetuned_classification_zh"
model_after_finetune = PeftModel.from_pretrained(base_model_for_inference, peft_model_id)

# 将LoRA权重合并到基础模型中，并卸载LoRA模块
model_after_finetune = model_after_finetune.merge_and_unload()
model_after_finetune.eval()

print("微调后模型加载并合并完成。")

# 进行微调后评估
evaluate_classification(model_after_finetune, tokenizer, test_samples, phase="调整后")

print("\n===== 中文分类任务微调前后对比完成 =====")