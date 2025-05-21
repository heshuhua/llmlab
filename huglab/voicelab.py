from transformers import pipeline
transcriber = pipeline(task="automatic-speech-recognition", model="openai/whisper-small")
text = transcriber("data/audio/mlk.flac")
text