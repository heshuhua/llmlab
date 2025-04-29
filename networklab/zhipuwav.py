from langchain_community.chat_models.zhipuai import ChatZhipuAI
client = ZhipuAI()  # 填写您自己的APIKey
with open("asr1.wav", "rb") as audio_file:
    transcriptResponse = client.audio.transcriptions.create(
        model="glm-asr",
        file=audio_file,
        stream=False
    )
    for item in transcriptResponse:
        print(item)