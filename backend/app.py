from flask import Flask, request, jsonify
import cv2
import numpy as np
import io
import sys
import os
import base64
from pathlib import Path
from flask_cors import CORS
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.gesture_recognizer import GestureRecognizer

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

# Initialize the gesture recognizer
gesture_recognizer = GestureRecognizer()

def decode_base64_image(base64_string):
    """Decode base64 image data to numpy array."""
    try:
        # Remove data URL prefix if present
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]
        
        # Decode base64 string
        img_bytes = base64.b64decode(base64_string)
        logger.info(f"Decoded base64 string, length: {len(img_bytes)} bytes")
        
        # Convert to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        logger.info(f"Converted to numpy array, shape: {nparr.shape}")
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
            
        logger.info(f"Successfully decoded image, shape: {img.shape}")
        return img
    except Exception as e:
        logger.error(f"Error decoding base64 image: {str(e)}")
        raise

@app.route('/process_frame', methods=['POST', 'OPTIONS'])
def process_frame():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        logger.info("Received frame processing request")
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data in request")
            return jsonify({'success': False, 'results': {'error': 'No JSON data provided'}}), 400
            
        if 'frame' not in data:
            logger.error("No frame data in request")
            return jsonify({'success': False, 'results': {'error': 'No frame data provided'}}), 400
            
        # Get the frame data
        frame_data = data['frame']
        logger.info("Processing frame for gesture detection")
        
        # Decode the base64 image
        try:
            img = decode_base64_image(frame_data)
            logger.info(f"Successfully decoded image for processing, shape: {img.shape}")
        except Exception as e:
            logger.error(f"Failed to decode image: {str(e)}")
            return jsonify({'success': False, 'results': {'error': f'Invalid image data: {str(e)}'}}), 400
        
        # Process gestures
        try:
            detected_gestures = gesture_recognizer.detect_gestures(img)
            logger.info(f"Raw detected gestures: {detected_gestures}")
            
            # Ensure we have a list of gestures
            if isinstance(detected_gestures, str):
                gesture_list = [detected_gestures]
            elif isinstance(detected_gestures, list):
                gesture_list = detected_gestures
            else:
                gesture_list = []
            
            response_data = {
                'success': True,
                'results': {
                    'gestures': gesture_list,
                    'error': None
                }
            }
            logger.info(f"Sending response: {response_data}")
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error during gesture detection: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'results': {
                    'gestures': [],
                    'error': f"Gesture detection error: {str(e)}"
                }
            })
            
    except Exception as e:
        logger.error(f"Unexpected error in process_frame: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'results': {
                'error': f"Server error: {str(e)}"
            }
        }), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000) 