from rapidocr import RapidOCR

engine = RapidOCR()

img_url = "/Users/heshuhua/lab/ailab/llmlab/testa.jpg"
#result = engine(img_url,use_det=False, use_cls=False, use_rec=True)
result = engine(img_url)
#print(result)
print(result.to_paddleocr_format)


result.vis("test_bak.jpg")