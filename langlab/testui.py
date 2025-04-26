import gradio as gr
import time  # For simulating speech-to-text and backend delay
import random  # For simulating backend response
from flask import Flask,request,jsonify
from vosk import KaldiRecognizer, Model
import json,re
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.chains.router import MultiPromptChain
from langchain_ollama import OllamaLLM
from langchain.chains import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE

model = Model('/Users/heshuhua/lab/ailab/voicelab/vosk-model-small-cn-0.22')
def transcribe(stream, new_chunk):

    sample_rate, audio_data = new_chunk
    audio_data = audio_data.tobytes()

    if stream is None:
        rec = KaldiRecognizer(model, sample_rate)
        result = []
    else:
        rec, result = stream

    if rec.AcceptWaveform(audio_data):
        text_result = json.loads(rec.Result())["text"]
        if text_result != "":
            result.append(text_result)
        partial_result = ""
    else:
        partial_result = json.loads(rec.PartialResult())["partial"] + " "

    return (rec, result), "\n".join(result) + "\n" + partial_result




withdraw_template = """你是银行资深柜员，非常善于处理客户取款问题。
你会从输入信息中判断出是谁来做业务，给出客户姓名 username=客户姓名
你会判断客户到银行做的是什么交易，识别出取款交易给设置当前的 pcode=200101。
你会从问题中识别出客户要取多少钱，比如取3000， 那amount=3000。
你会从客户是否是代为他人办理，如果是代办，需要设置agent=true，如果是本人办理或没有识别出来，则设置agent=false

这是一个客户业务：
{input}

请只输出 username,pcode，amount，agent的信息
"""


despoit_template =  """你是银行资深柜员，非常善于处理客户存款问题。
你会从输入信息中判断出是谁来做业务，给出客户姓名 username=李四
你会判断客户到银行做的是什么交易，识别出存款交易给设置当前的 pcode=200102。
你会从问题中识别出客户要存多少钱，比如存3000， 那amount=3000。

这是一个客户业务：
{input}

请只输出 username,pcode和amount的信息
"""

prompt_infos = [
    {
        "name": "存款",
        "description": "适用于回答存款问题",
        "prompt_template": despoit_template,
    },
    {
        "name": "取款",
        "description": "适用于回答取款问题",
        "prompt_template": withdraw_template,
    },
]

llm = OllamaLLM(model="llama3.1:latest",temperature=0.9)
#llm = OllamaLLM(model="deepseek-r1:32b",temperature=0.9)


destination_chains = {}
# 遍历prompt_infos列表，为每个信息创建一个LLMChain。
for p_info in prompt_infos:
    name = p_info["name"]  # 提取名称
    prompt_template = p_info["prompt_template"]  # 提取模板
    # 创建PromptTemplate对象
    prompt = PromptTemplate(template=prompt_template, input_variables=["input"])
    # 使用上述模板和llm对象创建LLMChain对象
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # 将新创建的chain对象添加到destination_chains字典中
    destination_chains[name] = chain

# 创建一个默认的ConversationChain
default_chain = ConversationChain(llm=llm, output_key="text")

# 从prompt_infos中提取目标信息并将其转化为字符串列表
destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
# 使用join方法将列表转化为字符串，每个元素之间用换行符分隔
destinations_str = "\n".join(destinations)
# 根据MULTI_PROMPT_ROUTER_TEMPLATE格式化字符串和destinations_str创建路由模板
router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
# 创建路由的PromptTemplate
router_prompt = PromptTemplate(
    template=router_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)
# 使用上述路由模板和llm对象创建LLMRouterChain对象
router_chain = LLMRouterChain.from_llm(llm, router_prompt)
# 创建MultiPromptChain对象，其中包含了路由链，目标链和默认链。
chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=destination_chains,
    default_chain=default_chain,
    verbose=True,
)

def getResult(text):
    print('getresult-'+text)
    username_match = re.search(r"username\s*=\s*(\w+)", text)
    print(username_match)
    pcode_match = re.search(r"pcode\s*=\s*(\w+)", text)
    print(pcode_match)
    amount_match = re.search(r"amount\s*=\s*(\d+)", text)
    print(amount_match)
    agent_match = re.search(r"agent\s*=\s*(true|false)", text)
    print(agent_match)

    result = {}

    if username_match:
        result['username'] = username_match.group(1)
    if pcode_match:
        result['pcode'] = pcode_match.group(1)
    if amount_match:
        result['amount'] = int(amount_match.group(1))
    if agent_match:
        result['agent'] = agent_match.group(1) == 'true'
    print(result)

    json_output = json.dumps(result, ensure_ascii=False, indent=4)
    return(json_output)

def fake_speech_to_text(speech_input):
    """Simulates speech-to-text conversion."""
    time.sleep(2)  # Simulate processing time
    return f"Translated: {speech_input}"

def populate_edit_box(translated_text):
    """Populates the middle edit textbox with the translated text."""
    return translated_text

def call_backend_for_withdrawal(edited_text):
    """Simulates calling the backend system for withdrawal and returns a string."""
    time.sleep(1.5)  # Simulate backend processing
    # In a real scenario, you would connect to your backend here
    # and process the edited_text to determine the withdrawal amount.
    # For this example, we'll just return a simulated response.
    llmResult = chain(edited_text)
    print("1----")
    print(llmResult)
    print("2----")
    tmpstr=llmResult['text']
    print(tmpstr)
    print("3----")
    withdrawal_info = f"'{tmpstr}'."
    return gr.update(value=withdrawal_info, visible=True), gr.update(visible=False)

def toggle_deposit_withdraw(show_deposit):
    """Toggles the visibility of deposit and withdraw textboxes."""
    return gr.update(visible=show_deposit), gr.update(visible=not show_deposit)

biztxt = gr.Textbox()
with gr.Blocks() as demo:
    gr.Markdown("## 语音业w务")

    gr.Interface(
    fn=transcribe,
    inputs=[
        "state", gr.Audio(sources=["microphone"], type="numpy", streaming=True),
    ],
    outputs=[
        "state", biztxt,
    ],
    live=True)

    
    
    with gr.Row():
        manual_edit_c = gr.Textbox(label="Edit Translation", placeholder="You can edit the translated text here...")
        confirm_button_d = gr.Button("确认")

    confirm_button_d.click(
        fn=lambda x: x,
        inputs=biztxt,
        outputs=manual_edit_c,
        queue=False  # Immediate update
    )

    gr.Markdown("---")

    with gr.Row():
        show_deposit_button = gr.Button("存款")
        show_withdraw_button = gr.Button("取款")

    deposit_amount_f = gr.Textbox(label="Deposit", visible=False)
    withdraw_amount_e = gr.Textbox(label="取款", visible=True)

    submit_button_g = gr.Button("提交")
    submit_button_g.click(
        fn=call_backend_for_withdrawal,
        inputs=manual_edit_c,
        outputs=[withdraw_amount_e, deposit_amount_f]
    )

    is_deposit_visible = gr.State(False)  # State to track which textbox is visible

    show_deposit_button.click(
        fn=lambda: True,
        outputs=is_deposit_visible,
        queue=False  # Immediate update
    ).then(
        fn=toggle_deposit_withdraw,
        inputs=is_deposit_visible,
        outputs=[deposit_amount_f, withdraw_amount_e],
        queue=False
    )

    show_withdraw_button.click(
        fn=lambda: False,
        outputs=is_deposit_visible,
        queue=False  # Immediate update
    ).then(
        fn=toggle_deposit_withdraw,
        inputs=is_deposit_visible,
        outputs=[deposit_amount_f, withdraw_amount_e],
        queue=False
    )

    #speech_input_a.change(fn=fake_speech_to_text, inputs=speech_input_a, outputs=translated_text_b)

demo.launch()