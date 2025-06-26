from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 指定模型名称
model_name = "Qwen/Qwen1.5-0.5B"

# 加载分词器
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 加载模型
# device_map="auto" 会自动将模型加载到可用的设备（如 GPU）上
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

# 确保模型处于评估模式
model.eval()

print("===== 调整前模型加载完成 =====")

# 测试调整前的模型
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
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=100,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95
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

print("\n===== 调整前模型输出示例 =====")
for i, prompt in enumerate(prompts_before):
    print(f"\n--- 问题 {i+1}: {prompt} ---")
    response_before = generate_response(prompt, model, tokenizer)
    print(f"模型回答: {response_before}")