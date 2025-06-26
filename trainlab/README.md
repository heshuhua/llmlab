# LLaMA3 + LoRA 服务部署（Mac）

## 安装依赖
```bash
pip install -r requirements.txt
```

## 启动服务
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 测试接口
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "范廷颂是什么时候去世的？"}'
```

> 请确保你将 `base_model_name` 和 `lora_path` 替换为你本地的模型路径。