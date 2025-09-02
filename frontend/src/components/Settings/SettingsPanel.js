import React, { useState } from 'react';
import './SettingsPanel.css';

const SettingsPanel = ({ 
  settings, 
  onSettingsChange, 
  onClearMemory,
  isVisible,
  onClose 
}) => {
  const [parentalGateOpen, setParentalGateOpen] = useState(false);
  const [mathAnswer, setMathAnswer] = useState('');
  const [mathProblem, setMathProblem] = useState(null);
  const [gateAttempts, setGateAttempts] = useState(0);

  const generateMathProblem = () => {
    const a = Math.floor(Math.random() * 10) + 1;
    const b = Math.floor(Math.random() * 10) + 1;
    const operations = ['+', '-'];
    const op = operations[Math.floor(Math.random() * operations.length)];
    
    let answer;
    if (op === '+') {
      answer = a + b;
    } else {
      // Ensure no negative results for subtraction
      const larger = Math.max(a, b);
      const smaller = Math.min(a, b);
      answer = larger - smaller;
      return { question: `${larger} ${op} ${smaller}`, answer };
    }
    
    return { question: `${a} ${op} ${b}`, answer };
  };

  const openParentalGate = () => {
    const problem = generateMathProblem();
    setMathProblem(problem);
    setParentalGateOpen(true);
    setMathAnswer('');
    setGateAttempts(0);
  };

  const checkParentalGate = () => {
    const userAnswer = parseInt(mathAnswer);
    if (userAnswer === mathProblem.answer) {
      setParentalGateOpen(false);
      setGateAttempts(0);
      return true;
    } else {
      setGateAttempts(prev => prev + 1);
      if (gateAttempts >= 2) {
        // Generate new problem after 3 failed attempts
        const newProblem = generateMathProblem();
        setMathProblem(newProblem);
        setGateAttempts(0);
        alert('Too many incorrect attempts. Here\'s a new problem.');
      } else {
        alert('Incorrect answer. Please try again.');
      }
      setMathAnswer('');
      return false;
    }
  };

  const handleClearMemory = () => {
    if (checkParentalGate()) {
      onClearMemory?.();
      alert('Learning memory has been cleared successfully.');
    }
  };

  const handleSettingChange = (key, value) => {
    onSettingsChange?.({ ...settings, [key]: value });
  };

  if (!isVisible) return null;

  return (
    <div className="settings-overlay">
      <div className="settings-panel">
        <div className="settings-header">
          <h2>⚙️ Settings</h2>
          <button onClick={onClose} className="close-btn" aria-label="Close settings">✕</button>
        </div>

        {parentalGateOpen ? (
          <div className="parental-gate">
            <div className="gate-header">
              <h3>🔒 Parental Verification Required</h3>
              <p>Please solve this math problem to access parental controls:</p>
            </div>
            
            <div className="math-problem">
              <div className="problem-display">
                <span className="problem-text">{mathProblem.question} = ?</span>
              </div>
              
              <div className="answer-input">
                <input
                  type="number"
                  value={mathAnswer}
                  onChange={(e) => setMathAnswer(e.target.value)}
                  placeholder="Enter answer"
                  autoFocus
                  onKeyPress={(e) => e.key === 'Enter' && checkParentalGate()}
                />
                <button onClick={checkParentalGate} className="submit-btn">
                  Submit
                </button>
              </div>
              
              <div className="gate-attempts">
                Attempts: {gateAttempts}/3
              </div>
            </div>
            
            <div className="gate-actions">
              <button 
                onClick={() => {
                  setParentalGateOpen(false);
                  setGateAttempts(0);
                }} 
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="settings-content">
            <div className="settings-section">
              <h3>🎤 Audio Settings</h3>
              
              <label className="setting-item">
                <div className="setting-label">
                  <input
                    type="checkbox"
                    checked={settings.micEnabled}
                    onChange={(e) => handleSettingChange('micEnabled', e.target.checked)}
                  />
                  <span>Enable Microphone</span>
                </div>
                <small>Allow voice input for speech practice</small>
              </label>
              
              <label className="setting-item">
                <div className="setting-label">
                  <span>Voice Volume</span>
                  <span className="volume-display">{settings.volume}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={settings.volume}
                  onChange={(e) => handleSettingChange('volume', parseInt(e.target.value))}
                  className="volume-slider"
                />
              </label>
            </div>

            <div className="settings-section">
              <h3>📹 Camera Settings</h3>
              
              <label className="setting-item">
                <div className="setting-label">
                  <input
                    type="checkbox"
                    checked={settings.cameraEnabled}
                    onChange={(e) => handleSettingChange('cameraEnabled', e.target.checked)}
                  />
                  <span>Enable Camera</span>
                </div>
                <small>Allow camera for letter recognition activities</small>
              </label>
            </div>

            <div className="settings-section">
              <h3>🎯 Learning Settings</h3>
              
              <label className="setting-item">
                <div className="setting-label">
                  <span>Difficulty Level</span>
                </div>
                <select
                  value={settings.difficulty}
                  onChange={(e) => handleSettingChange('difficulty', e.target.value)}
                  className="difficulty-select"
                >
                  <option value="easy">🟢 Easy - Basic letters</option>
                  <option value="medium">🟡 Medium - Letters + sounds</option>
                  <option value="hard">🔴 Hard - Advanced phonics</option>
                </select>
              </label>
              
              <label className="setting-item">
                <div className="setting-label">
                  <input
                    type="checkbox"
                    checked={settings.phonicsMode}
                    onChange={(e) => handleSettingChange('phonicsMode', e.target.checked)}
                  />
                  <span>Phonics Focus Mode</span>
                </div>
                <small>Emphasize letter sounds and pronunciation</small>
              </label>

              <label className="setting-item">
                <div className="setting-label">
                  <input
                    type="checkbox"
                    checked={settings.adaptiveLearning}
                    onChange={(e) => handleSettingChange('adaptiveLearning', e.target.checked)}
                  />
                  <span>Adaptive Learning</span>
                </div>
                <small>Adjust difficulty based on child's progress</small>
              </label>
            </div>

            <div className="settings-section privacy-section">
              <h3>🔒 Privacy & Safety</h3>
              
              <div className="privacy-info">
                <p>✅ No data sharing with third parties</p>
                <p>✅ COPPA compliant - designed for children</p>
                <p>✅ All conversations stay on your device</p>
              </div>
            </div>

            <div className="settings-section parental-controls">
              <h3>👨‍👩‍👧‍👦 Parental Controls</h3>
              
              <button 
                onClick={openParentalGate}
                className="danger-btn"
              >
                🗑️ Clear Learning Memory
              </button>
              <small className="warning-text">
                ⚠️ This will permanently delete all progress and conversation history
              </small>
            </div>

            <div className="settings-footer">
              <small>KidSafe Alphabet Tutor v1.0 - Built with privacy in mind</small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPanel;
