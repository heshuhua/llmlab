import gradio as gr
import time  # For simulating speech-to-text and backend delay
import random  # For simulating backend response
from flask import Flask,request,jsonify
import audiomodel
import appln
import json,re

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
    llmResult = appln.chain(edited_text)
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
    gr.Markdown("## 语音业务")

    gr.Interface(
    fn=audiomodel.transcribe,
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

    with gr.Row() as bizarea:
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