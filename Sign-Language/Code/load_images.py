import cv2
import numpy as np
import os, pickle, random
from sklearn.model_selection import train_test_split

def get_image_size():
    img = cv2.imread('gestures/1/100.jpg', 0)
    return img.shape

def get_num_of_classes():
    return len(os.listdir('gestures'))

image_x, image_y = get_image_size()
num_of_classes = get_num_of_classes()

def load_images():
    images = []
    labels = []
    for i in range(num_of_classes):
        gesture_folder = f'gestures/{i}'
        for img_file in os.listdir(gesture_folder):
            img_path = os.path.join(gesture_folder, img_file)
            img = cv2.imread(img_path, 0)
            images.append(img)
            labels.append(i)
    return np.array(images), np.array(labels)

images, labels = load_images()
train_images, val_images, train_labels, val_labels = train_test_split(images, labels, test_size=0.2, random_state=42)

with open('train_images', 'wb') as f:
    pickle.dump(train_images, f)
with open('train_labels', 'wb') as f:
    pickle.dump(train_labels, f)
with open('val_images', 'wb') as f:
    pickle.dump(val_images, f)
with open('val_labels', 'wb') as f:
    pickle.dump(val_labels, f)
print('Image data split and saved.') 