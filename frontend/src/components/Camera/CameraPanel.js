import React, { useState, useRef, useEffect } from 'react';
import './CameraPanel.css';

const CameraPanel = ({ onLetterDetected, isEnabled = true }) => {
  const [isActive, setIsActive] = useState(false);
  const [detectedLetter, setDetectedLetter] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    if (isActive && isEnabled) {
      startCamera();
    } else {
      stopCamera();
    }
    
    return () => stopCamera();
  }, [isActive, isEnabled]);

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'environment' // Use back camera if available
        } 
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Camera access denied:', error);
      setError('Camera access denied. Please allow camera permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const captureAndRecognize = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      // Capture frame from video
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const ctx = canvas.getContext('2d');
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);
      
      // Convert to base64
      const imageData = canvas.toDataURL('image/jpeg', 0.8);
      
      // Send to backend for recognition
      const response = await fetch('http://localhost:8000/api/vision/recognize-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          image_data: imageData,
          session_id: 'default'
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setDetectedLetter(result.letter || 'Unknown');
        setConfidence(result.confidence || 0);
        onLetterDetected?.(result.letter, result.confidence);
      } else {
        throw new Error('Recognition service unavailable');
      }
    } catch (error) {
      console.error('Letter recognition failed:', error);
      setError('Recognition failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="camera-panel">
      <div className="camera-header">
        <h3>📷 Letter Recognition</h3>
        <button 
          onClick={() => setIsActive(!isActive)}
          className={`camera-toggle ${isActive ? 'active' : ''}`}
          disabled={!isEnabled}
        >
          {isActive ? '🛑 Stop Camera' : '📹 Start Camera'}
        </button>
      </div>
      
      <div className="camera-content">
        {!isEnabled ? (
          <div className="camera-disabled">
            <div className="status-icon">📵</div>
            <p>Camera disabled in settings</p>
            <small>Enable camera in Settings to use letter recognition</small>
          </div>
        ) : error ? (
          <div className="camera-error">
            <div className="status-icon">⚠️</div>
            <p>{error}</p>
            <button onClick={() => setIsActive(false)} className="retry-btn">
              Try Again
            </button>
          </div>
        ) : isActive ? (
          <div className="camera-active">
            <div className="video-container">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                muted
                className="camera-video"
              />
              <div className="camera-overlay">
                <div className="focus-frame">
                  <div className="corner top-left"></div>
                  <div className="corner top-right"></div>
                  <div className="corner bottom-left"></div>
                  <div className="corner bottom-right"></div>
                </div>
                <div className="instruction">Hold letter in frame</div>
              </div>
            </div>
            
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            
            <div className="camera-controls">
              <button 
                onClick={captureAndRecognize}
                disabled={isProcessing}
                className={`recognize-btn ${isProcessing ? 'processing' : ''}`}
              >
                {isProcessing ? (
                  <>
                    <span className="spinner"></span>
                    Processing...
                  </>
                ) : (
                  <>
                    🔍 Recognize Letter
                  </>
                )}
              </button>
            </div>
            
            {detectedLetter && (
              <div className="detection-result">
                <div className="result-header">Detection Result:</div>
                <div className="detected-letter">
                  <span className="letter-display">{detectedLetter}</span>
                </div>
                <div className="confidence">
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${confidence * 100}%` }}
                    ></div>
                  </div>
                  <span className="confidence-text">
                    {(confidence * 100).toFixed(1)}% confident
                  </span>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="camera-preview">
            <div className="camera-placeholder">
              <div className="placeholder-icon">📹</div>
              <p>Click "Start Camera" to begin letter recognition</p>
              <small>Point camera at printed letters A-Z</small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CameraPanel;
