from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from peft import PeftModel
import torch

# 模型 ID（你本地已有）
model_id = "meta-llama/Meta-Llama-3-8B"

import os
os.makedirs("./offload", exist_ok=True)

#import os
#os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

device = torch.device("cpu")


# 输入：你自定义的中文问答内容
question = "李白的代表作有哪些？"
context = "李白是唐代著名诗人，有《将进酒》《静夜思》等代表作，被称为诗仙。"

# 构造 prompt（模仿训练格式）
prompt = f"问：{question}\n上下文：{context}\n答："

# === 加载 tokenizer ===
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token  # 防止推理时 padding 报错

# === 推理函数 ===
def generate_answer(model, title="模型输出"):
    print(f"\n—— {title} ——")
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(answer.replace(prompt, "").strip())

# === 加载未微调的原始模型 ===
base_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    #device_map={"": "cpu"},
    device_map=None,
    torch_dtype=torch.float16,
    offload_folder="./offload",        # ✅ 必须参数
    offload_state_dict=True    
).to(device)
base_model.eval()

generate_answer(base_model, title="微调前（原始模型）")

# === 加载已微调的模型（LoRA 权重） ===
lora_model_path = "./lora-llama3-zhqa-debug"
lora_model = PeftModel.from_pretrained(base_model, lora_model_path).to(device)
lora_model.eval()

generate_answer(lora_model, title="微调后（LoRA 适配模型）")
