import gradio as gr

def toggle_group(show):
    return gr.update(visible=show)

with gr.Blocks() as demo:
    show_checkbox = gr.Checkbox(label="Show Group")
    with gr.Group(visible=False) as my_group:
        gr.Markdown("This content is in the group.")
        text_in_group = gr.Textbox(label="Text in Group")

    show_checkbox.change(
        fn=toggle_group,
        inputs=show_checkbox,
        outputs=my_group  # The gr.Group itself is the output for visibility
    )

demo.launch()