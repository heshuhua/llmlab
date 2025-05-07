import cv2
pic = cv2.imread("/Users/heshuhua/lab/ailab/llmlab/cvlab/dog.png")
cv2.imshow('title',pic)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(pic)