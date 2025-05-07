import json,re
from vosk import KaldiRecognizer, Model

#50M
model = Model('/Users/heshuhua/lab/ailab/voicelab/vosk-model-small-cn-0.22')

#1.3G
#model = Model('/Users/heshuhua/lab/ailab/voicelab/vosk-model-cn-0.22')
def transcribe(stream, new_chunk):

    sample_rate, audio_data = new_chunk
    audio_data = audio_data.tobytes()

    if stream is None:
        rec = KaldiRecognizer(model, sample_rate)
        result = []
    else:
        rec, result = stream

    if rec.AcceptWaveform(audio_data):
        text_result = json.loads(rec.Result())["text"]
        if text_result != "":
            result.append(text_result)
        partial_result = ""
    else:
        partial_result = json.loads(rec.PartialResult())["partial"] + " "

    return (rec, result), "\n".join(result) + "\n" + partial_result,"\n".join(result) + "\n" + partial_result
