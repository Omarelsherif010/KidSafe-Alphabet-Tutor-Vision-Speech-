import React from 'react';
import './ProgressStrip.css';

const ProgressStrip = ({ progress }) => {
  const { heardCorrectly = 0, needsPractice = 0, sessionStreak = 0 } = progress;

  return (
    <div className="progress-strip">
      <div className="progress-badge correct">
        <div className="badge-icon">✅</div>
        <div className="badge-content">
          <div className="badge-count">{heardCorrectly}</div>
          <div className="badge-label">Heard Correctly</div>
        </div>
      </div>

      <div className="progress-badge practice">
        <div className="badge-icon">📚</div>
        <div className="badge-content">
          <div className="badge-count">{needsPractice}</div>
          <div className="badge-label">Needs Practice</div>
        </div>
      </div>

      <div className="progress-badge streak">
        <div className="badge-icon">🔥</div>
        <div className="badge-content">
          <div className="badge-count">{sessionStreak}</div>
          <div className="badge-label">Session Streak</div>
        </div>
      </div>

      {/* Achievement badges */}
      {sessionStreak >= 5 && (
        <div className="achievement-badge">
          <div className="achievement-icon">🌟</div>
          <div className="achievement-text">On Fire!</div>
        </div>
      )}

      {heardCorrectly >= 10 && (
        <div className="achievement-badge">
          <div className="achievement-icon">🏆</div>
          <div className="achievement-text">Star Student!</div>
        </div>
      )}
    </div>
  );
};

export default ProgressStrip;
