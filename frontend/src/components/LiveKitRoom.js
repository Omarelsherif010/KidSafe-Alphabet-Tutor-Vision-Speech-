import React, { useState, useRef } from 'react';
import { Room, RoomEvent, RemoteParticipant } from 'livekit-client';

const LiveKitRoom = ({ 
  onConnectionChange,
  onConversationUpdate,
  onLetterChange,
  onAgentSpeakingChange,
  onProgressUpdate,
  onDerivedStateUpdate,
  settings = {}
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('disconnected');
  const [currentLetter, setCurrentLetter] = useState('A');
  const [conversation, setConversation] = useState([]);
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
  const [userSpeech, setUserSpeech] = useState('');
  const [progress, setProgress] = useState({
    heardCorrectly: 0,
    needsPractice: 0,
    sessionStreak: 0
  });
  
  const roomRef = useRef(null);
  const audioElementRef = useRef(null);

  // LiveKit connection parameters (you can get these from your LiveKit dashboard)
  const LIVEKIT_URL = process.env.REACT_APP_LIVEKIT_URL || 'wss://kidsafe-alphabet-tutor-4ky10bll.livekit.cloud';
  const ROOM_NAME = 'room2';

  // Generate access token from backend
  const generateToken = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/livekit-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          room_name: ROOM_NAME,
          participant_name: 'child' 
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Token generated successfully');
        return data.token;
      } else {
        const error = await response.json();
        console.error('Token generation failed:', error);
        throw new Error(error.detail || 'Token generation failed');
      }
    } catch (error) {
      console.error('Token generation error:', error);
      throw error;
    }
  };

  const connectToRoom = async () => {
    try {
      setConnectionState('connecting');
      console.log('📊 Initial progress state:', progress);
      console.log('💬 Initial conversation state:', conversation);
      
      const token = await generateToken();
      if (!token) {
        setConnectionState('failed');
        return;
      }

      const newRoom = new Room();
      roomRef.current = newRoom;
      
      // Room event listeners
      newRoom.on(RoomEvent.Connected, () => {
        console.log('✅ Connected to LiveKit room');
        setIsConnected(true);
        setConnectionState('connected');
        onConnectionChange?.(true);
      });
      
      newRoom.on(RoomEvent.Disconnected, () => {
        console.log('❌ Disconnected from room');
        setIsConnected(false);
        setConnectionState('disconnected');
        onConnectionChange?.(false);
      });
      
      newRoom.on(RoomEvent.ParticipantConnected, (participant) => {
        console.log('👤 Participant joined:', participant.identity);
        if (participant.identity.includes('agent')) {
          console.log('🤖 AI Tutor joined the room');
        }
      });
      
      newRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        console.log('🎵 Track subscribed:', track.kind, participant.identity);
        
        if (track.kind === 'audio' && participant instanceof RemoteParticipant) {
          console.log('🔊 Agent audio track received');
          setIsAgentSpeaking(true);
          onAgentSpeakingChange?.(true);
          
          // Attach audio track to audio element for playback
          if (audioElementRef.current) {
            track.attach(audioElementRef.current);
          }
          
          // Reset speaking indicator after a delay
          setTimeout(() => {
            setIsAgentSpeaking(false);
            onAgentSpeakingChange?.(false);
          }, 3000);
        }
      });
      
      newRoom.on(RoomEvent.DataReceived, (payload, participant) => {
        try {
          const data = JSON.parse(new TextDecoder().decode(payload));
          console.log('📨 RAW Data received from', participant.identity, ':', data);
          console.log('📨 Participant identity check:', participant.identity, 'vs child');
          
          // Only process data from the agent, not from ourselves
          if (participant.identity !== 'child') {
            console.log('📨 Processing data from agent:', participant.identity);
            
            if (data.type === 'agent_speech') {
              console.log('🤖 Agent speech received:', {
                text: data.text,
                letter: data.current_letter,
                progress: data.progress
              });
              
              setConversation(prev => {
                const newConv = [...prev, {
                  type: 'agent',
                  text: data.text,
                  timestamp: Date.now(),
                  letter: data.current_letter
                }];
                console.log('🔄 Calling onConversationUpdate with:', newConv);
                onConversationUpdate?.(newConv);
                return newConv;
              });
              
              const newLetter = data.current_letter || currentLetter;
              setCurrentLetter(newLetter);
              onLetterChange?.(newLetter);
              
              // Update derived state if provided
              if (data.derived_state) {
                onDerivedStateUpdate?.(data.derived_state);
              }
              
              // Update progress based on agent analysis
              if (data.progress) {
                console.log('📊 Updating progress based on agent analysis:', data.progress);
                console.log('📊 Current progress before update:', progress);
                
                if (data.progress.is_correct) {
                  setProgress(prev => {
                    const newProgress = {
                      ...prev,
                      heardCorrectly: prev.heardCorrectly + 1,
                      sessionStreak: prev.sessionStreak + 1
                    };
                    console.log('🔄 Calling onProgressUpdate with:', newProgress);
                    onProgressUpdate?.(newProgress);
                    return newProgress;
                  });
                } else if (data.progress.needs_practice) {
                  setProgress(prev => {
                    const newProgress = {
                      ...prev,
                      needsPractice: prev.needsPractice + 1,
                      sessionStreak: 0
                    };
                    console.log('🔄 Calling onProgressUpdate with:', newProgress);
                    onProgressUpdate?.(newProgress);
                    return newProgress;
                  });
                }
              } else {
                console.log('⚠️ No progress data received from agent');
              }
            } else if (data.type === 'user_speech') {
              console.log('🎤 User speech received:', {
                text: data.text,
                interim: data.interim,
                letter: data.current_letter
              });
              
              setUserSpeech(data.text);
              if (!data.interim) {
                setConversation(prev => {
                  const newConv = [...prev, {
                    type: 'user',
                    text: data.text,
                    timestamp: Date.now()
                  }];
                  onConversationUpdate?.(newConv);
                  return newConv;
                });
              }
            }
          } else {
            console.log('🚫 Ignoring data from child participant (ourselves)');
          }
        } catch (e) {
          console.error('Error parsing room data:', e);
        }
      });
      
      // Connect to the room
      await newRoom.connect(LIVEKIT_URL, token);
      
      // Enable microphone for child speech
      await newRoom.localParticipant.enableCameraAndMicrophone(false, true);
      console.log('🎤 Microphone enabled and publishing');
      
    } catch (error) {
      console.error('❌ Connection failed:', error);
      setConnectionState('failed');
    }
  };
  
  const disconnectFromRoom = async () => {
    if (roomRef.current) {
      await roomRef.current.disconnect();
      roomRef.current = null;
      setIsConnected(false);
      setConnectionState('disconnected');
      setConversation([]);
      setUserSpeech('');
      onConnectionChange?.(false);
      onConversationUpdate?.([]);
    }
  };

  return (
    <>
      <style>{`
        .livekit-room {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        
        .connection-section {
          background: rgba(255, 255, 255, 0.95);
          border-radius: 20px;
          padding: 30px;
          color: #333;
          box-shadow: 0 10px 30px rgba(0,0,0,0.2);
          margin-bottom: 20px;
        }
        
        .connection-status {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 20px;
          font-size: 16px;
        }
        
        .status-indicator {
          font-size: 20px;
        }
        
        .status-text {
          font-weight: bold;
        }
        
        .connection-controls {
          text-align: center;
        }
        
        .connect-btn {
          background: linear-gradient(45deg, #4CAF50, #45a049);
          color: white;
          padding: 15px 30px;
          border: none;
          border-radius: 25px;
          font-size: 18px;
          cursor: pointer;
          box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
          transition: all 0.3s;
        }
        
        .connect-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        
        .disconnect-btn {
          background: #f44336;
          color: white;
          padding: 15px 30px;
          border: none;
          border-radius: 25px;
          font-size: 18px;
          cursor: pointer;
          box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
          transition: all 0.3s;
        }
        
        .disconnect-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(244, 67, 54, 0.4);
        }
        
        .user-speech-display {
          background: #f8f9fa;
          border-radius: 10px;
          padding: 20px;
          margin-top: 20px;
        }
        
        .user-speech-display h4 {
          margin: 0 0 10px 0;
          color: #2196F3;
        }
        
        .user-speech-display p {
          background: white;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          padding: 15px;
          margin: 0;
          font-size: 16px;
          color: #333;
          font-weight: 500;
        }
      `}</style>
      
      <div className="livekit-room">
        <div className="connection-section">
          <div className="connection-status">
            <span className={`status-indicator ${connectionState}`}>
              {connectionState === 'connected' && '🟢'}
              {connectionState === 'connecting' && '🟡'}
              {connectionState === 'disconnected' && '🔴'}
              {connectionState === 'failed' && '❌'}
            </span>
            <span className="status-text">
              {connectionState === 'connected' && 'Connected to AI Tutor'}
              {connectionState === 'connecting' && 'Connecting...'}
              {connectionState === 'disconnected' && 'Not Connected'}
              {connectionState === 'failed' && 'Connection Failed'}
            </span>
          </div>
          
          <div className="connection-controls">
            {!isConnected ? (
              <button onClick={connectToRoom} className="connect-btn">
                🎤 Start Learning
              </button>
            ) : (
              <button onClick={disconnectFromRoom} className="disconnect-btn">
                🛑 Stop Learning
              </button>
            )}
          </div>
        </div>

        {userSpeech && (
          <div className="user-speech-display">
            <h4>🎤 You said:</h4>
            <p>"{userSpeech}"</p>
          </div>
        )}

        {/* Test buttons for debugging data flow */}
        {isConnected && (
          <div className="test-controls" style={{marginTop: '20px', padding: '15px', background: '#f0f8ff', borderRadius: '10px'}}>
            <h4>🧪 Test Data Flow</h4>
            <button 
              onClick={() => {
                const testConversation = [{
                  type: 'user',
                  text: 'Test user speech',
                  timestamp: Date.now()
                }, {
                  type: 'agent', 
                  text: 'Great job! That was correct!',
                  timestamp: Date.now(),
                  letter: currentLetter
                }];
                setConversation(testConversation);
                onConversationUpdate?.(testConversation);
              }}
              style={{margin: '5px', padding: '8px 16px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}
            >
              ✅ Test Correct Answer
            </button>
            <button 
              onClick={() => {
                const newProgress = {
                  heardCorrectly: progress.heardCorrectly + 1,
                  needsPractice: progress.needsPractice,
                  sessionStreak: progress.sessionStreak + 1
                };
                setProgress(newProgress);
                onProgressUpdate?.(newProgress);
              }}
              style={{margin: '5px', padding: '8px 16px', background: '#2196F3', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}
            >
              📊 Test Progress Update
            </button>
            <button 
              onClick={() => {
                const testConversation = [{
                  type: 'user',
                  text: 'Test wrong answer',
                  timestamp: Date.now()
                }, {
                  type: 'agent',
                  text: 'Let\'s try that again! Remember, the letter A makes the "ah" sound.',
                  timestamp: Date.now(),
                  letter: currentLetter
                }];
                setConversation(testConversation);
                onConversationUpdate?.(testConversation);
                
                const newProgress = {
                  heardCorrectly: progress.heardCorrectly,
                  needsPractice: progress.needsPractice + 1,
                  sessionStreak: 0
                };
                setProgress(newProgress);
                onProgressUpdate?.(newProgress);
              }}
              style={{margin: '5px', padding: '8px 16px', background: '#f44336', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}
            >
              ❌ Test Wrong Answer
            </button>
            <button 
              onClick={() => {
                if (roomRef.current) {
                  // Send a test message to the agent to trigger a response
                  const testData = {
                    type: 'user_message',
                    text: 'Hello agent, can you hear me?',
                    timestamp: Date.now()
                  };
                  roomRef.current.localParticipant.publishData(
                    JSON.stringify(testData),
                    { reliable: true }
                  );
                  console.log('📤 Sent test message to agent');
                }
              }}
              style={{margin: '5px', padding: '8px 16px', background: '#9C27B0', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}
            >
              📞 Ping Agent
            </button>
          </div>
        )}

        {/* Hidden audio element for agent speech playback */}
        <audio ref={audioElementRef} autoPlay />
      </div>
    </>
  );
};

export default LiveKitRoom;
