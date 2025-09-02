import React from 'react';
import './MemoryPanel.css';

const MemoryPanel = ({ 
  conversationHistory = [], 
  derivedState = {},
  isVisible = true 
}) => {
  if (!isVisible) return null;

  const { child_name, current_letter, difficulty } = derivedState;
  const lastSixTurns = conversationHistory.slice(-6);

  return (
    <div className="memory-panel">
      <div className="memory-header">
        <h3>🧠 Memory Panel</h3>
        <div className="memory-info">Last 3 conversation pairs</div>
      </div>

      <div className="memory-content">
        <div className="conversation-memory">
          <h4>💬 Recent Conversation:</h4>
          <div className="memory-turns">
            {lastSixTurns.length > 0 ? (
              lastSixTurns.map((turn, index) => (
                <div key={index} className={`memory-turn ${turn.type}`}>
                  <span className="turn-speaker">
                    {turn.type === 'user' ? '👤' : '🤖'}
                  </span>
                  <span className="turn-text">
                    {turn.text.length > 40 
                      ? `${turn.text.substring(0, 40)}...` 
                      : turn.text
                    }
                  </span>
                </div>
              ))
            ) : (
              <div className="no-memory">No conversation yet - start talking!</div>
            )}
          </div>
        </div>

        <div className="derived-state">
          <h4>📊 Derived State:</h4>
          <div className="state-items">
            <div className="state-item">
              <span className="state-label">Name:</span>
              <span className="state-value">{child_name || 'Not provided'}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Current Letter:</span>
              <span className="state-value letter">{current_letter || 'A'}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Difficulty:</span>
              <span className="state-value">{difficulty || 'Easy'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryPanel;
