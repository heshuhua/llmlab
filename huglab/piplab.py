from transformers import pipeline
pipe = pipeline("sentiment-analysis")
print(pipe("today is shinning"))