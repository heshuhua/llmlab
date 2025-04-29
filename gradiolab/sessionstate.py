import gradio as gr

def store_messages(message:str,history:list[str]):
    output={
        "Cur meg":message,
        "Pre megs":history[::1]
    }
    history.append(message)
    return output,history
demo = gr.Interface(
    fn=store_messages,
    inputs=["textbox",gr.State(value=[])],
    outputs=["json",gr.State()]
)
demo.launch()