import React, { useState, useEffect } from 'react';
import LiveKitRoom from '../LiveKitRoom';
import LessonCard from '../Lesson/LessonCard';
import ProgressStrip from '../Progress/ProgressStrip';
import MemoryPanel from '../Memory/MemoryPanel';
import SettingsPanel from '../Settings/SettingsPanel';
import CameraPanel from '../Camera/CameraPanel';
import AvatarBubble from '../Avatar/AvatarBubble';
import './App.css';

const App = () => {
  // Core state
  const [isConnected, setIsConnected] = useState(false);
  const [currentLetter, setCurrentLetter] = useState('A');
  const [conversation, setConversation] = useState([]);
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
  const [derivedState, setDerivedState] = useState({});
  
  // Progress tracking
  const [progress, setProgress] = useState({
    heardCorrectly: 0,
    needsPractice: 0,
    sessionStreak: 0
  });
  
  // UI state
  const [showSettings, setShowSettings] = useState(false);
  const [showMemory, setShowMemory] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  
  // Settings state
  const [settings, setSettings] = useState({
    micEnabled: true,
    cameraEnabled: true,
    volume: 80,
    difficulty: 'medium',
    phonicsMode: true,
    adaptiveLearning: true
  });

  // Current lesson data
  const [lessonData, setLessonData] = useState({
    phoneme: 'ah',
    examples: ['Apple', 'Ant', 'Airplane'],
    activity: "Can you find something in the room that starts with the letter A?",
    progress: 0
  });

  // Update lesson data when letter changes
  useEffect(() => {
    const letterData = {
      'A': { phoneme: 'ah', examples: ['Apple', 'Ant', 'Airplane'], activity: "Find something that starts with A!" },
      'B': { phoneme: 'buh', examples: ['Ball', 'Banana', 'Bear'], activity: "Buzz like a bee: B-b-b!" },
      'C': { phoneme: 'kuh', examples: ['Cat', 'Car', 'Cake'], activity: "Click your tongue for the C sound!" },
      'D': { phoneme: 'duh', examples: ['Dog', 'Duck', 'Door'], activity: "Tap your tongue for D!" },
      'E': { phoneme: 'eh', examples: ['Elephant', 'Egg', 'Eye'], activity: "Say 'eh' like you're surprised!" },
      'F': { phoneme: 'fuh', examples: ['Fish', 'Flower', 'Fire'], activity: "Bite your lip and say 'fuh'!" }
    };
    
    const data = letterData[currentLetter] || letterData['A'];
    const letterIndex = currentLetter.charCodeAt(0) - 'A'.charCodeAt(0);
    const progressPercent = (letterIndex / 25) * 100;
    
    setLessonData({
      ...data,
      progress: progressPercent
    });
  }, [currentLetter]);

  const handleConversationUpdate = (newConversation) => {
    console.log('App: Conversation updated:', newConversation);
    setConversation(newConversation);
  };

  const handleProgressUpdate = (newProgress) => {
    console.log('App: Progress updated:', newProgress);
    setProgress(newProgress);
  };

  const handleLetterChange = (newLetter) => {
    console.log('App: Letter changed to:', newLetter);
    setCurrentLetter(newLetter);
  };

  const handleAgentSpeakingChange = (speaking) => {
    console.log('App: Agent speaking state:', speaking);
    setIsAgentSpeaking(speaking);
  };

  const handleDerivedStateUpdate = (newState) => {
    console.log('App: Derived state updated:', newState);
    setDerivedState(newState);
  };

  // Camera panel handlers
  const handleLetterDetected = (letter, confidence) => {
    console.log('App: Letter detected:', letter, 'confidence:', confidence);
    if (confidence > 0.7) {
      // If detected letter matches current lesson, provide positive feedback
      if (letter === currentLetter) {
        console.log('Correct letter detected!');
      } else {
        // Update current letter if different
        setCurrentLetter(letter);
      }
    }
  };

  const handleSettingsChange = (newSettings) => {
    console.log('App: Settings changed:', newSettings);
    setSettings(newSettings);
  };

  const handleClearMemory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/session/default/memory', {
        method: 'DELETE'
      });
      if (response.ok) {
        setConversation([]);
        setProgress({ heardCorrectly: 0, needsPractice: 0, sessionStreak: 0 });
        setDerivedState({});
        console.log('Memory cleared successfully');
      }
    } catch (error) {
      console.error('Failed to clear memory:', error);
    }
  };

  return (
    <div className="app">
      <div className="app-header">
        <h1>🎯 KidSafe Alphabet Tutor</h1>
        <div className="header-controls">
          <button 
            onClick={() => setShowMemory(!showMemory)}
            className="control-button memory-toggle"
          >
            🧠 {showMemory ? 'Hide' : 'Show'} Memory
          </button>
          <button 
            onClick={() => setShowSettings(true)}
            className="control-button settings-button"
          >
            ⚙️ Settings
          </button>
        </div>
      </div>

      <div className="app-content">
        {/* Avatar Section */}
        <AvatarBubble 
          isAgentSpeaking={isAgentSpeaking}
          currentLetter={currentLetter}
        />

        {/* Progress Strip */}
        <ProgressStrip progress={progress} />

        {/* Main Content Grid */}
        <div className="content-grid">
          <div className="left-panel">
            <LessonCard 
              currentLetter={currentLetter}
              lessonData={lessonData}
              progress={progress}
            />
          </div>

          <div className="center-panel">
            <LiveKitRoom 
              onConversationUpdate={handleConversationUpdate}
              onProgressUpdate={handleProgressUpdate}
              onLetterChange={handleLetterChange}
              onAgentSpeakingChange={handleAgentSpeakingChange}
              onDerivedStateUpdate={handleDerivedStateUpdate}
              settings={settings}
            />
          </div>

          <div className="right-panel">
            {showCamera && (
              <CameraPanel 
                onLetterDetected={handleLetterDetected}
                isEnabled={settings.cameraEnabled}
              />
            )}
            
            {showMemory && (
              <MemoryPanel 
                conversation={conversation}
                derivedState={derivedState}
                onClose={() => setShowMemory(false)}
              />
            )}
          </div>
        </div>
      </div>

      {showSettings && (
        <SettingsPanel 
          settings={settings}
          onSettingsChange={handleSettingsChange}
          onClearMemory={handleClearMemory}
          isVisible={showSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
};

export default App;
