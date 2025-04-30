from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg19 import preprocess_input
import os
import numpy as np

app = Flask(__name__)

# Load the model at startup
model_path = 'model/yale_vgg19_model.h5'
if os.path.exists(model_path):
    model = load_model(model_path)
    print("Model loaded successfully!")
else:
    print(f"Error: Model file not found at {model_path}")
    model = None

# Define emotion classes
emotion_classes = [
    "centerlight", "glasses", "happy", "leftlight", "noglasses", 
    "normal", "rightlight", "sad", "sleepy", "surprised", "wink"
]

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    try:
        # Get the image file
        image_file = request.files['image']
        
        # Load and preprocess the image
        img = load_img(image_file)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Make prediction
        prediction = model.predict(img_array)
        predicted_class_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][predicted_class_idx])
        
        # Get the emotion label
        emotion = emotion_classes[predicted_class_idx]
        
        # Get top 3 predictions
        top_indices = np.argsort(prediction[0])[-3:][::-1]
        top_predictions = {
            emotion_classes[idx]: float(prediction[0][idx])
            for idx in top_indices
        }
        
        return jsonify({
            "emotion": emotion,
            "confidence": confidence,
            "top_predictions": top_predictions
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This route receives emotion from the frontend (OpenCV script)
@app.route('/update_emotion', methods=['POST'])
def update_emotion():
    data = request.json
    print("Received emotion:", data['emotion']) 
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(debug=True)
