import cv2
import os

gestures_dir = 'gestures'
for gesture_id in os.listdir(gestures_dir):
    gesture_path = os.path.join(gestures_dir, gesture_id)
    if os.path.isdir(gesture_path):
        for img_file in os.listdir(gesture_path):
            img_path = os.path.join(gesture_path, img_file)
            img = cv2.imread(img_path)
            flipped = cv2.flip(img, 1)
            new_img_path = os.path.join(gesture_path, 'flip_' + img_file)
            cv2.imwrite(new_img_path, flipped)
print('All images flipped and saved.') 