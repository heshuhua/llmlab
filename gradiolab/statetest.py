import gradio as gr

scores=[]

def track_score(score):
    scores.append(score)
    top_scores = sorted(scores,reverse=True)[:3]
    return top_scores
demo = gr.Interface(
    track_score,
    gr.Number(label="score"),
    gr.JSON(label="top score")
).launch()