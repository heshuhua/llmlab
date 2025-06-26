from fastapi import FastAPI
from pydantic import BaseModel
from model_loader import model, tokenizer
import torch

app = FastAPI()

class Query(BaseModel):
    prompt: str
    max_new_tokens: int = 128

@app.post("/generate")
def generate_text(query: Query):
    inputs = tokenizer(query.prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=query.max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    result = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"response": result}