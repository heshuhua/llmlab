import os
import cv2
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from pathlib import Path

recogizer=cv2.face.LBPHFaceRecognizer_create()
recogizer.read('/Users/heshuhua/lab/ailab/llmlab/cvlab/trainer/trainer.yml')

names=["heshuhua"]
idn = [1]

def face_detect_demo(img):
    #未转成，
    #gray=cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    gray=cv2.cvtColor(img,cv2.CV_16F)
     
    #调用人脸识别
    face_detector=cv2.CascadeClassifier('/opt/anaconda3/envs/dgai/lib/python3.12/site-packages/cv2/data/haarcascade_frontalface_default.xml')

    #读取人脸特征
    face=face_detector.detectMultiScale(gray,1.1,5,0,(100,100),(800,800))

    for x,y,w,h in face:
        #标记
        cv2.rectangle(img,(x,y),(x+w,y+h),color=(0,0,255),thickness=2)

        ids,confidence=recogizer.predict(gray[y:y+h,x:x+w])

        if confidence >60:
            print("heshuhua ")
        else:
            print("not recgonize")
    cv2.imshow('result',img)

cap=cv2.VideoCapture(0)

while True:
    flag,frame=cap.read()
    if not flag:
        break
    face_detect_demo(frame)
    if ord(' ')==cv2.waitKey(10):
        break
cv2.destroyAllWindows()
cap.release()