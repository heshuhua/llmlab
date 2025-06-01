import gradio as gr
import time
from datetime import datetime
import audiomodel
import appln
#import appmodel
import resutil
import json

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

#persontran=appmodel.Deposit
def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def add_message(history, message):
    for x in message["files"]:
        history.append({"role": "user", "content": {"path": x}})
    if message["text"] is not None:
        history.append({"role": "user", "content": message["text"]})
    #appln.chain(message["text"])
    #appmodel.chain(message["text"])
    #persontran=appmodel.chain.invoke({"text",message["text"]})
    #return history, gr.MultimodalTextbox(value=None, interactive=False),appmodel.chain.invoke({"text",message["text"]})  #使用Person对象
    return history, gr.MultimodalTextbox(value=None, interactive=False),appln.chain(message["text"])


manual_edit_c = gr.Textbox(label="交易信息", placeholder="You can edit the translated text here...")

def bot(history: list):
    response = "**That's cool!**"
    #response = manual_edit_c["text"]
    history.append({"role": "assistant", "content": ""})
    for character in response:
        history[-1]["content"] += character
        #time.sleep(0.05)
        yield history

def bizhandle():
    print("调用---")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"开始调用------当前时间 (时:分:秒): {current_time}")
    cardRec

with gr.Blocks() as cardRec:
    gr.Textbox(label="身份识别")
with gr.Blocks() as withDrawTx:
    gr.Textbox(label="取款")

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            #biz_feedback = gr.Textbox(label="交易信息", placeholder="You can edit the translated text here...",lines=20)
            @gr.render(inputs=manual_edit_c)
            def show_cardRec(text):
                print(f"模型返回 --------{text}")
                
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(f"模型返回调用------当前时间 (时:分:秒): {current_time}")
                pcode = resutil.extract_pcode(text)
                amount = resutil.extract_amount(text)
                print(f"提取-------{text} --------{pcode}")
                #jsonstr= json.dumps(jsonstr, ensure_ascii=False, indent=4)
                
                
                if pcode == '200101':
                    print(f"add --------{pcode}")
                    if(resutil.convert_string_to_integer(amount)>=5000):
                        gr.Markdown("## 需要身份识别")
                        output_video = gr.Video(label="Processed Video", streaming=True, autoplay=True)
                    gr.Textbox(label=f"取款交易",value=30)
                    gr.Textbox(label=f"取款人")
                    gr.Textbox(label=f"取款金额",value=f"{amount}")
                    gr.Checkbox(label="是否代理人", info="代理人需要验证代理人身份?"),
                else:
                    gr.Textbox(label=f"存款交易")
                    gr.Textbox(label=f"存款人")
                    gr.Textbox(label=f"存款金额")
        
        with gr.Column():
            chatbot = gr.Chatbot(elem_id="chatbot", bubble_full_width=False, type="messages")

            chat_input = gr.MultimodalTextbox(
                interactive=True,
                file_count="multiple",
                placeholder="Enter message or upload file...",
                show_label=False,
                sources=["microphone", "upload"],
            )

            chat_msg = chat_input.submit(
                add_message, [chatbot, chat_input], [chatbot, chat_input,manual_edit_c]
            )
            bot_msg = chat_msg.then(bot, chatbot, chatbot, api_name="bot_response")
            bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

            manual_edit_c.change(bizhandle)

            chatbot.like(print_like_dislike, None, None, like_user_message=True)

            gr.Interface(fn=audiomodel.transcribe,inputs=["state", gr.Audio(sources=["microphone"], type="numpy", streaming=True),],outputs=["state", manual_edit_c,chat_input],live=True)

demo.launch()
