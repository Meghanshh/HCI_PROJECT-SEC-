import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg19 import preprocess_input
import cv2
import tensorflow as tf

def main():
    print("Testing VGG19 model...")
    
    # Check if model exists
    model_path = 'model/yale_vgg19_model.h5'
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return
    
    # Load model
    try:
        model = load_model(model_path)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return
    
    # Check if processed images exist
    processed_dir = 'model/processed_yale'
    if not os.path.exists(processed_dir):
        print(f"Error: Processed images directory not found at {processed_dir}")
        return
    
    # Find a sample image
    sample_images = [f for f in os.listdir(processed_dir) if f.endswith('.jpg')]
    if not sample_images:
        print("Error: No sample images found in the processed directory")
        return
    
    sample_image = sample_images[0]
    img_path = os.path.join(processed_dir, sample_image)
    
    # Define emotion classes
    emotion_classes = [
        "centerlight", "glasses", "happy", "leftlight", "noglasses", 
        "normal", "rightlight", "sad", "sleepy", "surprised", "wink"
    ]
    
    # Load and preprocess the image
    try:
        img = load_img(img_path)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Make prediction
        prediction = model.predict(img_array)
        predicted_class_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][predicted_class_idx])
        
        # Get the emotion label
        emotion = emotion_classes[predicted_class_idx]
        
        print(f"Test successful!")
        print(f"Sample image: {sample_image}")
        print(f"Predicted emotion: {emotion}")
        print(f"Confidence: {confidence:.4f}")
        
        # Get top 3 predictions
        top_indices = np.argsort(prediction[0])[-3:][::-1]
        print("\nTop 3 predictions:")
        for idx in top_indices:
            print(f"{emotion_classes[idx]}: {prediction[0][idx]:.4f}")
        
    except Exception as e:
        print(f"Error during prediction: {str(e)}")

if __name__ == "__main__":
    main() 