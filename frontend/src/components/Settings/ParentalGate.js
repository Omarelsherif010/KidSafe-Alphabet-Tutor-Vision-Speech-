import React, { useState, useEffect } from 'react';
import './ParentalGate.css';

const ParentalGate = ({ onSuccess }) => {
  const [challenge, setChallenge] = useState({ question: '', answer: '' });
  const [userAnswer, setUserAnswer] = useState('');
  const [attempts, setAttempts] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    generateChallenge();
  }, []);

  const generateChallenge = () => {
    const a = Math.floor(Math.random() * 10) + 1;
    const b = Math.floor(Math.random() * 10) + 1;
    setChallenge({
      question: `What is ${a} + ${b}?`,
      answer: (a + b).toString()
    });
    setUserAnswer('');
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (userAnswer.trim() === challenge.answer) {
      onSuccess();
    } else {
      setAttempts(prev => prev + 1);
      setError('Incorrect answer. Please try again.');
      
      if (attempts >= 2) {
        generateChallenge();
        setAttempts(0);
      }
    }
  };

  return (
    <div className="parental-gate">
      <div className="gate-header">
        <h3>🔒 Parental Verification</h3>
        <p>Please solve this simple math problem to access settings:</p>
      </div>

      <form onSubmit={handleSubmit} className="gate-form">
        <div className="challenge-question">
          {challenge.question}
        </div>
        
        <input
          type="number"
          value={userAnswer}
          onChange={(e) => setUserAnswer(e.target.value)}
          placeholder="Enter answer"
          className="answer-input"
          autoFocus
        />
        
        {error && (
          <div className="error-message">{error}</div>
        )}
        
        <div className="gate-buttons">
          <button type="submit" className="submit-button">
            Submit
          </button>
          <button 
            type="button" 
            onClick={generateChallenge}
            className="new-question-button"
          >
            New Question
          </button>
        </div>
      </form>

      <div className="gate-info">
        <small>This verification helps ensure only parents can change settings.</small>
      </div>
    </div>
  );
};

export default ParentalGate;
