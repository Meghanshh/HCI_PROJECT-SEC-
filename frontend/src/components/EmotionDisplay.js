import React, { useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const EMOTION_COLORS = {
  'Angry': '#ff4d4d',
  'Disgust': '#ff9933',
  'Fear': '#ffff4d',
  'Happy': '#4dff4d',
  'Sad': '#4d4dff',
  'Surprise': '#ff4dff',
  'Neutral': '#ffffff'
};

const EMOTION_ICONS = {
  'Angry': '😠',
  'Disgust': '🤢',
  'Fear': '😨',
  'Happy': '😊',
  'Sad': '😢',
  'Surprise': '😮',
  'Neutral': '😐'
};

const EmotionDisplay = ({ emotionData, className }) => {
  const chartRef = useRef(null);
  const historyRef = useRef([]);
  const maxHistoryLength = 30; // 30 seconds of history

  useEffect(() => {
    if (emotionData) {
      // Update emotion history
      const timestamp = new Date().toLocaleTimeString();
      historyRef.current.push({
        timestamp,
        ...emotionData
      });

      // Keep only last 30 entries
      if (historyRef.current.length > maxHistoryLength) {
        historyRef.current.shift();
      }

      // Update chart
      if (chartRef.current) {
        chartRef.current.update();
      }
    }
  }, [emotionData]);

  const chartData = {
    labels: historyRef.current.map(entry => entry.timestamp),
    datasets: Object.keys(EMOTION_COLORS).map(emotion => ({
      label: emotion,
      data: historyRef.current.map(entry => entry.all_predictions?.[emotion] || 0),
      borderColor: EMOTION_COLORS[emotion],
      backgroundColor: `${EMOTION_COLORS[emotion]}33`,
      tension: 0.4
    }))
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    },
    plugins: {
      legend: {
        display: false
      }
    }
  };

  return (
    <div className={`emotion-display ${className}`}>
      <div className="current-emotion">
        <div className="emotion-icon" style={{ color: EMOTION_COLORS[emotionData?.emotion] }}>
          {EMOTION_ICONS[emotionData?.emotion] || '😶'}
        </div>
        <div className="emotion-details">
          <h3>{emotionData?.emotion || 'No emotion detected'}</h3>
          <div className="confidence-bar">
            <div 
              className="confidence-progress"
              style={{ 
                width: `${(emotionData?.confidence || 0) * 100}%`,
                backgroundColor: EMOTION_COLORS[emotionData?.emotion]
              }}
            />
          </div>
          <span className="confidence-text">
            Confidence: {((emotionData?.confidence || 0) * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="emotion-history">
        <h4>Emotion History</h4>
        <div className="chart-container">
          <Line ref={chartRef} data={chartData} options={chartOptions} />
        </div>
      </div>

      <div className="top-emotions">
        <h4>Top Emotions</h4>
        <div className="emotion-grid">
          {emotionData?.top3_emotions?.map(([emotion, confidence]) => (
            <div key={emotion} className="emotion-item">
              <span className="emotion-icon">{EMOTION_ICONS[emotion]}</span>
              <span className="emotion-label">{emotion}</span>
              <div className="mini-bar">
                <div 
                  className="mini-progress"
                  style={{ 
                    width: `${confidence * 100}%`,
                    backgroundColor: EMOTION_COLORS[emotion]
                  }}
                />
              </div>
              <span className="confidence-value">
                {(confidence * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EmotionDisplay; 