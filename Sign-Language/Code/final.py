import cv2
import numpy as np
import pickle
from keras.models import load_model
import os

def get_hand_hist():
    with open("hist", "rb") as f:
        hist = pickle.load(f)
    return hist

def get_image_size():
    img = cv2.imread('gestures/1/100.jpg', 0)
    return img.shape

def get_num_of_classes():
    return len(os.listdir('gestures'))

image_x, image_y = get_image_size()
num_of_classes = get_num_of_classes()
model = load_model('cnn_model_keras2.h5')
hist = get_hand_hist()

cam = cv2.VideoCapture(0)
x, y, w, h = 300, 100, 300, 300
while True:
    img = cam.read()[1]
    img = cv2.flip(img, 1)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([imgHSV], [0, 1], hist, [0, 180, 0, 256], 1)
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
    cv2.filter2D(dst,-1,disc,dst)
    blur = cv2.GaussianBlur(dst, (11,11), 0)
    blur = cv2.medianBlur(blur, 15)
    thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    thresh = cv2.merge((thresh,thresh,thresh))
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    thresh = thresh[y:y+h, x:x+w]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[1]
    if len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) > 5000:
            x1, y1, w1, h1 = cv2.boundingRect(contour)
            save_img = thresh[y1:y1+h1, x1:x1+w1]
            if w1 > h1:
                save_img = cv2.copyMakeBorder(save_img, int((w1-h1)/2) , int((w1-h1)/2) , 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
            elif h1 > w1:
                save_img = cv2.copyMakeBorder(save_img, 0, 0, int((h1-w1)/2) , int((h1-w1)/2) , cv2.BORDER_CONSTANT, (0, 0, 0))
            save_img = cv2.resize(save_img, (image_x, image_y))
            save_img = np.reshape(save_img, (1, image_x, image_y, 1))
            result = model.predict(save_img)
            prediction = np.argmax(result)
            cv2.putText(img, f'Prediction: {prediction}', (30, 60), cv2.FONT_HERSHEY_TRIPLEX, 2, (127, 255, 255))
    cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
    cv2.imshow("Gesture Recognition", img)
    if cv2.waitKey(1) == 27:
        break
cam.release()
cv2.destroyAllWindows() 