import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet_v2 import EfficientNetV2B0, preprocess_input
import matplotlib.pyplot as plt

# Load and preprocess the image
img_path = 'path_to_your_image.jpg'
img = image.load_img(img_path, target_size=(256, 256))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

print("Input shape:", x.shape)  # Should be (1, 256, 256, 3) for EfficientNetV2B0 