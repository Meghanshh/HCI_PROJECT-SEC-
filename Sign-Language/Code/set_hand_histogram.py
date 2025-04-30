import cv2
import numpy as np
import pickle
import os

print("\n=== DIRECTORY INFORMATION ===")
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")
script_dir = os.path.dirname(os.path.abspath(__file__))
hist_path = os.path.join(script_dir, "hist")
print(f"Histogram will be saved at: {hist_path}")
print("===========================\n")

def build_squares(img):
    x, y, w, h = 200, 80, 20, 20  # Start more left and higher, bigger boxes
    d = 8  # Slightly smaller gap
    imgCrop = None
    crop = None
    for i in range(8):  # 8 rows
        for j in range(12):  # 12 columns
            if np.any(imgCrop == None):
                imgCrop = img[y:y+h, x:x+w]
            else:
                imgCrop = np.hstack((imgCrop, img[y:y+h, x:x+w]))
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 1)
            x+=w+d
        if np.any(crop == None):
            crop = imgCrop
        else:
            crop = np.vstack((crop, imgCrop)) 
        imgCrop = None
        x = 200
        y+=h+d
    return crop

def get_hand_hist():
    cam = cv2.VideoCapture(0)  # Always use camera 0
    x, y, w, h = 300, 100, 300, 300
    flagPressedC, flagPressedS = False, False
    imgCrop = None
    while True:
        img = cam.read()[1]
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (640, 480))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        keypress = cv2.waitKey(1)
        if keypress == ord('c'):
            print("[INFO] 'c' pressed: Capturing hand histogram...")
            hsvCrop = cv2.cvtColor(imgCrop, cv2.COLOR_BGR2HSV)
            flagPressedC = True
            hist = cv2.calcHist([hsvCrop], [0, 1], None, [180, 256], [0, 180, 0, 256])
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        elif keypress == ord('s'):
            print("[INFO] 's' pressed: Saving histogram and exiting...")
            flagPressedS = True
            break
        if flagPressedC:
            dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)
            dst1 = dst.copy()
            disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
            cv2.filter2D(dst,-1,disc,dst)
            blur = cv2.GaussianBlur(dst, (11,11), 0)
            blur = cv2.medianBlur(blur, 15)
            ret,thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            thresh = cv2.merge((thresh,thresh,thresh))
            cv2.imshow("Thresh", thresh)
        if not flagPressedS:
            imgCrop = build_squares(img)
        cv2.imshow("Set hand histogram", img)
    cam.release()
    cv2.destroyAllWindows()
    with open(hist_path, "wb") as f:
        pickle.dump(hist, f)
        print(f"[INFO] Histogram saved at: {hist_path}")
        if os.path.exists(hist_path):
            print("[SUCCESS] File exists after saving!")
            print(f"File size: {os.path.getsize(hist_path)} bytes")
        else:
            print("[ERROR] File was not created!")

get_hand_hist() 