import React, { useState, useEffect } from 'react';
import './AvatarBubble.css';

const AvatarBubble = ({ isAgentSpeaking, currentLetter, currentText = '' }) => {
  const [mouthOpen, setMouthOpen] = useState(false);
  const [eyeBlink, setEyeBlink] = useState(false);

  // Animate mouth based on speech with lip-sync simulation
  useEffect(() => {
    if (isAgentSpeaking) {
      const interval = setInterval(() => {
        setMouthOpen(prev => !prev);
      }, 150 + Math.random() * 100); // Variable mouth animation for natural look
      return () => clearInterval(interval);
    } else {
      setMouthOpen(false);
    }
  }, [isAgentSpeaking]);

  // Random eye blinking for liveliness
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setEyeBlink(true);
      setTimeout(() => setEyeBlink(false), 150);
    }, 2000 + Math.random() * 3000);
    return () => clearInterval(blinkInterval);
  }, []);

  return (
    <div className="avatar-bubble">
      <div className={`avatar-face ${isAgentSpeaking ? 'speaking' : 'idle'}`}>
        <div className="avatar-eyes">
          <div className={`eye left-eye ${eyeBlink ? 'blink' : ''}`}>
            <div className="pupil"></div>
          </div>
          <div className={`eye right-eye ${eyeBlink ? 'blink' : ''}`}>
            <div className="pupil"></div>
          </div>
        </div>
        <div className={`avatar-mouth ${mouthOpen ? 'open' : 'closed'} ${isAgentSpeaking ? 'talking' : 'smiling'}`}>
          <div className="mouth-inner"></div>
          {isAgentSpeaking && (
            <div className="sound-waves">
              <span className="wave-1"></span>
              <span className="wave-2"></span>
              <span className="wave-3"></span>
            </div>
          )}
        </div>
      </div>
      
      {/* Speech bubble for current text */}
      {currentText && (
        <div className="speech-bubble">
          <div className="bubble-content">{currentText}</div>
          <div className="bubble-tail"></div>
        </div>
      )}
      
      <div className="avatar-letter-display">
        <span className="current-letter">{currentLetter}</span>
      </div>
      <div className="avatar-status">
        {isAgentSpeaking ? '🗣️ Speaking...' : '👂 Listening...'}
      </div>
    </div>
  );
};

export default AvatarBubble;
