import gradio as gr

def greet(name):
    return f"Hello, {name}!"

def goodbye(name):
    return f"Goodbye, {name}!"

with gr.Blocks() as demo:
    name_input = gr.Textbox(label="Name")
    greeting_output = gr.Textbox(label="Greeting")
    farewell_output = gr.Textbox(label="Farewell")
    greet_button = gr.Button("Greet")
    goodbye_button = gr.Button("Say Goodbye")

    greet_button.click(greet, inputs=name_input, outputs=greeting_output, api_name="greet_user")
    goodbye_button.click(goodbye, inputs=name_input, outputs=farewell_output, api_name="say_farewell")

demo.launch()