from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import cv2
import base64
import sys
import os
from pathlib import Path
import logging
import tensorflow as tf
import traceback

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Constants
MODEL_PATH = Path('../model/emotion_model.h5')
TARGET_SIZE = (256, 256)  # EfficientNetV2B0 input size
EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Load the model
model = None
try:
    if not MODEL_PATH.exists():
        logger.error(f"Model file not found at {MODEL_PATH}")
        logger.info("Please run the training script first: python train/quick_train.py")
    else:
        # Configure GPU memory growth
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Emotion detection model loaded successfully")
        logger.info(f"Model input shape: {model.input_shape}")
        logger.info(f"Model output shape: {model.output_shape}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    logger.error(traceback.format_exc())

def preprocess_image(image_data):
    """Preprocess image for emotion detection."""
    try:
        logger.info("Starting image preprocessing")
        
        # Convert base64 to image
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            encoded_data = image_data.split(',')[1]
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            img = image_data
            
        logger.info(f"Decoded image shape: {img.shape if img is not None else 'None'}")
        
        # Resize to target size (maintaining RGB)
        resized = cv2.resize(img, TARGET_SIZE)
        logger.info(f"Resized image shape: {resized.shape}")
        
        # Convert BGR to RGB (OpenCV uses BGR by default)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        logger.info(f"RGB image shape: {rgb.shape}")
        
        # Normalize pixel values to [0, 1]
        normalized = rgb.astype(np.float32) / 255.0
        logger.info(f"Normalized value range: [{normalized.min():.2f}, {normalized.max():.2f}]")
        
        # Reshape for model input
        processed = np.expand_dims(normalized, axis=0)
        logger.info(f"Final processed shape: {processed.shape}")
        
        return processed, None
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        logger.error(traceback.format_exc())
        return None, str(e)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        logger.info("Received frame processing request")
        
        if model is None:
            logger.error("Model not loaded")
            return jsonify({
                "success": False,
                "error": "Model not loaded. Please run the training script first."
            }), 500
            
        # Get data from request
        data = request.get_json()
        frame_data = data.get('frame')
        
        if not frame_data:
            logger.error("No frame data provided")
            return jsonify({
                "success": False,
                "error": "No frame data provided"
            }), 400
            
        # Process image
        processed_image, error = preprocess_image(frame_data)
        if error:
            logger.error(f"Image preprocessing failed: {error}")
            return jsonify({
                "success": False,
                "error": f"Image preprocessing failed: {error}"
            }), 500
            
        # Get predictions
        logger.info("Running model prediction")
        predictions = model.predict(processed_image, verbose=0)[0]
        logger.info(f"Raw predictions: {predictions}")
        
        # Get top emotion and confidence
        top_emotion_idx = np.argmax(predictions)
        top_emotion = EMOTIONS[top_emotion_idx]
        confidence = float(predictions[top_emotion_idx])
        logger.info(f"Top emotion: {top_emotion}, confidence: {confidence:.2f}")
        
        # Get top 3 emotions with confidences
        top3_indices = np.argsort(predictions)[-3:][::-1]
        top3_emotions = [
            (EMOTIONS[idx], float(predictions[idx]))
            for idx in top3_indices
        ]
        logger.info(f"Top 3 emotions: {top3_emotions}")
        
        # Prepare response
        results = {
            "emotion": top_emotion,
            "confidence": confidence,
            "all_predictions": {
                emotion: float(pred)
                for emotion, pred in zip(EMOTIONS, predictions)
            },
            "top3_emotions": top3_emotions
        }
        
        logger.info("Successfully processed frame")
        return jsonify({
            "success": True,
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    status = {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "emotions": EMOTIONS,
        "input_shape": TARGET_SIZE + (3,)
    }
    logger.info(f"Health check: {status}")
    return jsonify(status), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)