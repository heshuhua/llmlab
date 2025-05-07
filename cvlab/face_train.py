import numpy as np
import cv2 as cv
from PIL import Image
from pathlib import Path

def getImageAndLabel(path):
    facesSamples=[]
    ids=[]
    
    face_detect=cv.CascadeClassifier("/opt/anaconda3/envs/dgai/lib/python3.12/site-packages/cv2/data/haarcascade_frontalface_default.xml")

    for imagePath in Path(path).rglob("*"):

        #灰度打开照片
        PIL_img=Image.open(imagePath).convert('L')
        #照片转数组
        img_numpy=np.array(PIL_img,'uint8')
        #提取特征
        faces = face_detect.detectMultiScale(img_numpy)

        #文件名分割按.
        id= int(imagePath.stem.split("_")[0])
        #防止无脸数据
        for x,y,w,h in faces:
            ids.append(id)
            facesSamples.append(img_numpy[y:y+h,x:x+w])
    return facesSamples,ids


faces,ids=getImageAndLabel('/Users/heshuhua/lab/ailab/llmlab/cvlab/imgdata')

recognizer=cv.face.LBPHFaceRecognizer_create()

recognizer.train(faces,np.array(ids))
recognizer.write('/Users/heshuhua/lab/ailab/llmlab/cvlab/trainer/trainer.yml')

