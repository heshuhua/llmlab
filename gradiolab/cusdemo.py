import gradio as gr

def greet(name:str):
    return("hello,--"+name)

with gr.Blocks() as demo:
    name = gr.Textbox(label="Name")
    output =gr.Textbox(label="OBox",interactive=True)
    greet_bn = gr.Button("Greet")
    greet_bn.click(fn=greet,inputs=name,outputs=output,api_name="greet")
demo.launch()