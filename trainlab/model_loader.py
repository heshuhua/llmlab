from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

base_model_name = "meta-llama/Meta-Llama-3-8B"  # 替换为本地模型路径或名称
lora_path = "./lora-llama3-zhqa-debug"  # 替换为你的 LoRA 权重路径

tokenizer = AutoTokenizer.from_pretrained(base_model_name)

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map="auto",
    torch_dtype=torch.float16 if torch.backends.mps.is_available() else torch.float32
)

model = PeftModel.from_pretrained(base_model, lora_path)
model.eval()