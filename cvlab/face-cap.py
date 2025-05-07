import cv2 as cv
cap = cv.VideoCapture(0)
num =1
face_name="heshuhua"
face_id=1

while(cap.isOpened()):
    ret_flag,vshow=cap.read()
    cv.imshow("cap_test",vshow)
    #刷新频率
    k = cv.waitKey(1)&0xff

    if k == ord('s'):
        cv.imencode(".jpg",vshow)[1].tofile(f"/Users/heshuhua/lab/ailab/llmlab/cvlab/imgdata/{str(face_id)}_{face_name}_{str(num)}.jpg")
        print(f"保存第{str(num)}张照片")
        num +=1
    elif k == ord(' '):
        break
cap.release()
cv.destroyAllWindows()

