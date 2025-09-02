import React from 'react';
import './LessonCard.css';

const LessonCard = ({ 
  currentLetter, 
  phoneme, 
  examples, 
  activity, 
  progress 
}) => {
  return (
    <div className="lesson-card">
      <div className="lesson-header">
        <div className="letter-display">
          <span className="big-letter">{currentLetter}</span>
        </div>
        <div className="lesson-info">
          <h3>Letter {currentLetter}</h3>
          <div className="phoneme-display">
            Sound: <span className="phoneme">"{phoneme}"</span>
          </div>
        </div>
      </div>

      <div className="lesson-content">
        <div className="examples-section">
          <h4>📝 Example Words:</h4>
          <div className="example-words">
            {examples?.map((word, index) => (
              <span key={index} className="example-word">
                {word}
              </span>
            )) || `${currentLetter}pple, ${currentLetter}nt, ${currentLetter}irplane`}
          </div>
        </div>

        {activity && (
          <div className="activity-section">
            <h4>🎯 Activity:</h4>
            <div className="activity-text">
              {activity}
            </div>
          </div>
        )}
      </div>

      <div className="lesson-progress">
        <div className="progress-indicator">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progress || 0}%` }}
            ></div>
          </div>
          <span className="progress-text">{Math.round(progress || 0)}% Complete</span>
        </div>
      </div>
    </div>
  );
};

export default LessonCard;
