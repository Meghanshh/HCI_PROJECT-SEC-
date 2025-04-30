import React from 'react';

const SignLanguageDetector = ({ sign, confidence, isEnabled }) => {
  return (
    <div className="sign-language-container">
      <div className="sign-result">
        <p className="detected-sign">
          {sign ? `Detected: ${sign}` : 'No sign detected'}
        </p>
        {confidence > 0 && (
          <p className="confidence">
            Confidence: {(confidence * 100).toFixed(1)}%
          </p>
        )}
      </div>
      <div className="instructions">
        <h4>Instructions:</h4>
        <ul>
          <li>Show your hand clearly in the frame</li>
          <li>Make sure your hand is well-lit</li>
          <li>Try to keep your hand steady</li>
          <li>Supported gestures: goodluck, go_out, no, hi</li>
        </ul>
      </div>
    </div>
  );
};

export default SignLanguageDetector; 