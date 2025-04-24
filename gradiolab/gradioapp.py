import gradio as gr
from langlab import 

def greet(name):
    return "hello "+name +"!"

with gr.Blocks() as demo:
    gr.Markdown("## fancy")
    gr.Interface(fn=greet,inputs="text",outputs="text")
    


demo.launch()
    