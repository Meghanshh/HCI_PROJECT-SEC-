import React, { useState, useRef, useEffect } from 'react';
import { useTheme } from './contexts/ThemeContext';
import SignLanguageDetector from './components/SignLanguageDetector';
import './App.css';
import './styles/theme.css';

// Backend Configuration
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
const RECONNECT_DELAY = 3000;
const MAX_RECONNECT_DELAY = 30000;
const CONNECTION_CHECK_INTERVAL = 10000;

// Processing Configuration
const INITIAL_PROCESSING_INTERVAL = 1000;
const MIN_PROCESSING_INTERVAL = 500;
const MAX_PROCESSING_INTERVAL = 2000;
const MAX_RETRY_ATTEMPTS = 3;
const PROCESSING_TIMEOUT = 5000;
const ERROR_THRESHOLD = 3;

// Camera Configuration
const CAMERA_INIT_DELAY = 2000;
const TARGET_FPS = 24;
const TARGET_WIDTH = 640;
const TARGET_HEIGHT = 480;
const JPEG_QUALITY = 0.7;

// Performance Thresholds
const POOR_PERFORMANCE_THRESHOLD = 2000;
const FAIR_PERFORMANCE_THRESHOLD = 1000;
const FRAME_DROP_THRESHOLD = 100;

// Utility functions for connection and performance management
const getReconnectDelay = (attempts) => {
  return Math.min(RECONNECT_DELAY * Math.pow(2, attempts), MAX_RECONNECT_DELAY);
};

const updateConnectionQuality = (processingTime) => {
  if (processingTime > POOR_PERFORMANCE_THRESHOLD) return 'poor';
  if (processingTime > FAIR_PERFORMANCE_THRESHOLD) return 'fair';
  return 'good';
};

const adjustProcessingInterval = (processingTime) => {
  return Math.max(
    MIN_PROCESSING_INTERVAL,
    Math.min(MAX_PROCESSING_INTERVAL, processingTime * 1.5)
  );
};

const shouldProcessFrame = (lastProcessingTime, currentTime) => {
  return (currentTime - lastProcessingTime) >= FRAME_DROP_THRESHOLD;
};

function App() {
  const { isDarkMode, toggleTheme } = useTheme();
  const [mode, setMode] = useState('gesture');
  const [result, setResult] = useState({
    emotion: null,
    gesture: null,
    sign: null,
    confidence: 0,
    processingTime: 0
  });
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fps, setFps] = useState(0);
  const [resolution, setResolution] = useState({ width: 640, height: 480 });
  const [backendReady, setBackendReady] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const errorCountRef = useRef(0);
  const processingIntervalRef = useRef(null);
  const fpsCounterRef = useRef(0);
  const lastFpsUpdateRef = useRef(Date.now());
  const [connectionStatus, setConnectionStatus] = useState({
    connected: true,
    quality: 'good'
  });

  const [signDetection, setSignDetection] = useState({
    sign: null,
    confidence: 0,
    isEnabled: false
  });

  // Add new state for tracking processing attempts
  const processingAttemptsRef = useRef(0);
  const lastProcessingTimeRef = useRef(Date.now());

  // Initialize and cleanup
  useEffect(() => {
    let connectionInterval;
    
    const initializeApp = async () => {
      // First check backend connection
      const isConnected = await checkBackendConnection();
      
      if (isConnected) {
        // Wait for backend to be ready before starting camera
        setTimeout(async () => {
          if (backendReady) {
            await startCamera();
          }
        }, CAMERA_INIT_DELAY);
      }
    };

    // Start periodic connection checking
    connectionInterval = setInterval(async () => {
      await checkBackendConnection();
    }, CONNECTION_CHECK_INTERVAL);

    initializeApp();
    startFpsCounter();

    return () => {
      cleanup();
      clearInterval(connectionInterval);
    };
  }, [backendReady]);

  const startFpsCounter = () => {
    setInterval(() => {
      const now = Date.now();
      const elapsed = (now - lastFpsUpdateRef.current) / 1000;
      setFps(Math.round(fpsCounterRef.current / elapsed));
      fpsCounterRef.current = 0;
      lastFpsUpdateRef.current = now;
    }, 1000);
  };

  const cleanup = () => {
    stopCamera();
    if (processingIntervalRef.current) {
      clearInterval(processingIntervalRef.current);
    }
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }
  };

  const checkBackendConnection = async () => {
    try {
      console.log('Checking backend connection...');
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const healthResponse = await fetch(`${BACKEND_URL}/health`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (healthResponse.ok) {
        console.log('Backend health check successful');
        const connectionQuality = updateConnectionQuality(connectionStatus.lastProcessingTime || 0);
        setConnectionStatus(prev => ({
          ...prev,
          connected: true,
          lastError: null,
          reconnectAttempts: 0,
          lastSuccessfulConnection: Date.now(),
          connectionQuality
        }));
        
        setBackendReady(true);
        setError(null);
        errorCountRef.current = 0;
        return true;
      } else {
        console.error('Backend health check failed with status:', healthResponse.status);
        throw new Error('Backend health check failed');
      }
    } catch (err) {
      console.error('Connection error details:', {
        message: err.message,
        type: err.name,
        stack: err.stack
      });
      
      const reconnectDelay = getReconnectDelay(connectionStatus.reconnectAttempts);
      setConnectionStatus(prev => ({
        ...prev,
        connected: false,
        lastError: err.message,
        reconnectAttempts: prev.reconnectAttempts + 1,
        connectionQuality: 'poor',
        nextReconnectDelay: reconnectDelay
      }));
      
      setBackendReady(false);
      setError(`Cannot connect to server. Retrying in ${Math.round(reconnectDelay/1000)}s...`);

      // Schedule next reconnection attempt
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
      retryTimeoutRef.current = setTimeout(checkBackendConnection, reconnectDelay);
      
      return false;
    }
  };

  const startCamera = async () => {
    try {
      console.log('Starting camera initialization...');
      if (!backendReady) {
        console.warn('Backend not ready, cannot start camera');
        throw new Error('Backend not ready. Please wait...');
      }

      const constraints = {
        video: {
          width: { ideal: TARGET_WIDTH },
          height: { ideal: TARGET_HEIGHT },
          frameRate: { ideal: TARGET_FPS }
        }
      };

      console.log('Requesting camera access with constraints:', constraints);
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('Camera access granted');
      
      if (videoRef.current) {
        if (streamRef.current) {
          console.log('Stopping existing camera stream');
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        
        await new Promise((resolve) => {
          videoRef.current.onloadedmetadata = () => {
            const actualWidth = videoRef.current.videoWidth;
            const actualHeight = videoRef.current.videoHeight;
            console.log('Video metadata loaded:', { actualWidth, actualHeight });
            setResolution({
              width: actualWidth,
              height: actualHeight
            });
            resolve();
          };
        });

        try {
          console.log('Starting video playback');
          await videoRef.current.play();
          console.log('Video playback started successfully');
          setTimeout(() => {
            console.log('Starting frame processing');
            startProcessing();
          }, CAMERA_INIT_DELAY);
          return true;
        } catch (playError) {
          console.error('Video playback error:', playError);
          throw new Error(`Failed to start video playback: ${playError.message}`);
        }
      } else {
        console.error('Video element reference not found');
      }
    } catch (err) {
      console.error('Camera initialization error:', {
        message: err.message,
        type: err.name,
        stack: err.stack
      });
      setError(`Camera access error: ${err.message}`);
      return false;
    }
  };

  const stopCamera = () => {
    console.log('Stopping camera...');
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        console.log(`Stopping track: ${track.kind}`);
        track.stop();
      });
    }
    if (videoRef.current) {
      console.log('Clearing video source');
      videoRef.current.srcObject = null;
    }
  };

  const startProcessing = () => {
    if (processingIntervalRef.current) {
      clearInterval(processingIntervalRef.current);
    }
    processingIntervalRef.current = setInterval(processFrame, INITIAL_PROCESSING_INTERVAL);
  };

  const handleModeChange = (newMode) => {
    console.log('Switching mode to:', newMode);
    setMode(newMode);
    // Reset results when switching modes
    setResult({
      emotion: null,
      gesture: null,
      sign: null,
      confidence: 0,
      processingTime: 0
    });
    // Clear any existing errors
    setError(null);
  };

  const processFrame = async () => {
    if (!videoRef.current || !videoRef.current.srcObject || isProcessing) {
      return;
    }

    setIsProcessing(true);
    const now = Date.now();

    try {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0);

      // Convert the frame to base64
      const base64Frame = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
      const payload = {
        frame: base64Frame.split(',')[1],
        mode: mode  // Include the current mode in the request
      };

      console.log('Processing frame with mode:', mode);

      const processPromise = (async () => {
        try {
          const response = await fetch(`${BACKEND_URL}/process_frame`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const data = await response.json();
          console.log('Detection Results:', {
            mode,
            results: data.results,
            processingTime: Date.now() - now
          });
          
          if (!data.success) {
            throw new Error(data.error || 'Processing failed');
          }

          return data;
        } catch (error) {
          console.error('Request failed:', error);
          throw error;
        }
      })();

      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Processing timeout')), PROCESSING_TIMEOUT);
      });

      const data = await Promise.race([processPromise, timeoutPromise]);
      
      // Update results based on the current mode
      setResult(prev => {
        const newResult = { ...prev, processingTime: Date.now() - now };
        
        if (data.results) {
          if (mode === 'emotion') {
            newResult.emotion = data.results.emotion;
            newResult.confidence = data.results.confidence;
          } else if (mode === 'gesture') {
            const bestResult = Array.isArray(data.results) && data.results[0];
            newResult.gesture = bestResult ? bestResult.gesture : null;
            newResult.confidence = bestResult ? bestResult.confidence : 0;
          } else if (mode === 'sign') {
            newResult.sign = data.results.sign;
            newResult.confidence = data.results.confidence;
          } else if (mode === 'combined') {
            // Handle combined mode results
            if (data.results.emotion) newResult.emotion = data.results.emotion;
            if (data.results.gesture) newResult.gesture = data.results.gesture;
            if (data.results.sign) newResult.sign = data.results.sign;
          }
        }
        
        return newResult;
      });

      setError(null);
      processingAttemptsRef.current = 0;
      
    } catch (err) {
      console.error('Processing error:', err);
      setError(err.message);
      processingAttemptsRef.current++;
    } finally {
      setIsProcessing(false);
    }
  };

  const formatProcessingTime = (time) => {
    return time < 1000 ? `${Math.round(time)}ms` : `${(time/1000).toFixed(1)}s`;
  };

  return (
    <div className="app-container" data-theme={isDarkMode ? 'dark' : 'light'}>
      <header className="header">
        <div className="header-content">
          <h1>Expression Recognition System</h1>
          <button 
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDarkMode ? '🌞' : '🌙'}
          </button>
        </div>
        <div className="connection-status">
          <span className={`status ${connectionStatus.connected ? 'connected' : ''}`}>
            {connectionStatus.connected ? 'Connected' : 'Disconnected'}
          </span>
          <span className="quality">Quality: {connectionStatus.quality}</span>
        </div>
      </header>

      <div className="main-layout">
        <div className="video-section">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="video-feed"
          />
          {!connectionStatus.connected && (
            <div className="connection-error">
              Connection lost. Attempting to reconnect...
            </div>
          )}
        </div>

        <div className="right-panel">
          <div className="mode-buttons">
            <button 
              className={`mode-btn ${mode === 'combined' ? 'active' : ''}`}
              onClick={() => handleModeChange('combined')}
            >
              Combined
            </button>
            <button 
              className={`mode-btn ${mode === 'emotion' ? 'active' : ''}`}
              onClick={() => handleModeChange('emotion')}
            >
              Emotion
            </button>
            <button 
              className={`mode-btn ${mode === 'gesture' ? 'active' : ''}`}
              onClick={() => handleModeChange('gesture')}
            >
              Gesture
            </button>
            <button 
              className={`mode-btn ${mode === 'sign' ? 'active' : ''}`}
              onClick={() => handleModeChange('sign')}
            >
              Sign Language
            </button>
          </div>

          <div className="stats-section">
            <div className="stat-row">
              <div className="stat-group">
                <div className="stat-label">Processing Time</div>
                <div className="stat-value">{formatProcessingTime(result.processingTime)}</div>
              </div>
              <div className="stat-group">
                <div className="stat-label">Frame Rate</div>
                <div className="stat-value">{fps} FPS</div>
              </div>
            </div>

            <div className="stat-row">
              <div className="stat-group">
                <div className="stat-label">Resolution</div>
                <div className="stat-value">{resolution.width}x{resolution.height}</div>
              </div>
              <div className="stat-group">
                <div className="stat-label">Status</div>
                <div className="stat-value">{isProcessing ? 'Processing' : 'Ready'}</div>
              </div>
            </div>
          </div>

          <div className="detection-section">
            <h3>{mode === 'emotion' ? 'Emotion Detection' : 
                 mode === 'gesture' ? 'Gesture Detection' :
                 mode === 'sign' ? 'Sign Language Detection' :
                 'Combined Detection'}
            </h3>
            <div className="detection-result">
              {error ? (
                <div className="error">{error}</div>
              ) : mode === 'gesture' ? (
                result.gesture ? (
                  <div className="gesture-item">
                    {result.gesture} ({(result.confidence * 100).toFixed(1)}%)
                  </div>
                ) : (
                  <div className="no-detection">No gesture detected</div>
                )
              ) : mode === 'emotion' ? (
                result.emotion ? (
                  <div>{result.emotion}</div>
                ) : (
                  <div className="no-detection">No emotion detected</div>
                )
              ) : mode === 'sign' ? (
                result.sign ? (
                  <div>{result.sign}</div>
                ) : (
                  <div className="no-detection">No sign detected</div>
                )
              ) : (
                // Combined mode
                <div>
                  {result.emotion && <div>Emotion: {result.emotion}</div>}
                  {result.gesture && <div>Gesture: {result.gesture} ({(result.confidence * 100).toFixed(1)}%)</div>}
                  {result.sign && <div>Sign: {result.sign}</div>}
                  {!result.emotion && !result.gesture && !result.sign && (
                    <div className="no-detection">No detections</div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
