from gradio_client import Client

client = Client("http://127.0.0.1:7860/")

# 调用名为 "greet_user" 的 API 端点

result_greet = client.predict("World", api_name="/greet_user")
print(result_greet)

# 调用名为 "say_farewell" 的 API 端点
result_farewell = client.predict("Wddorld", api_name="/say_farewell")
print(result_farewell)