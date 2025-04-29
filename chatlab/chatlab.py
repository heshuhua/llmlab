import gradio as gr
import random


demo = gr.load_chat("http://localhost:11434/v1", model="llama3.1:latest")


demo.launch()