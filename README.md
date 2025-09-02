# KidSafe Alphabet Tutor - Vision & Speech

A real-time speech-to-speech AI tutor for teaching children the alphabet using voice interaction, computer vision, and child-optimized learning techniques. Built with COPPA compliance and safety-first design principles.

## 🎯 Features

- **Real-time Voice Interaction** - LiveKit-powered speech-to-speech communication
- **Child-Optimized Speech Recognition** - OpenAI Whisper STT optimized for young voices
- **Intelligent AI Tutor** - GPT-4 powered conversational learning with phonics coaching
- **Computer Vision** - Letter recognition from camera feed for visual learning
- **3-Turn Memory System** - Contextual conversation tracking for personalized learning
- **Progress Tracking** - Visual progress indicators and achievement system
- **COPPA Compliance** - Child safety protocols and parental controls
- **Sub-1.2s Response Time** - Optimized for real-time interaction

## 🏗️ Architecture

### Backend (FastAPI + LiveKit)
- **FastAPI** - High-performance async API framework
- **LiveKit Voice Agent** - Real-time audio streaming and processing
- **OpenAI Integration** - Whisper STT, GPT-4 LLM, OpenAI TTS
- **Modular Services** - Speech, vision, curriculum, safety, memory services
- **Token-based Authentication** - Secure room access for LiveKit sessions

### Frontend (React + LiveKit Client)
- **React** - Modern component-based UI framework
- **LiveKit Client** - Real-time audio/video communication
- **Responsive Design** - Child-friendly interface with visual feedback
- **Component Architecture** - Modular UI components for scalability

### Infrastructure
- **LiveKit Cloud** - Real-time communication infrastructure
- **Voice Activity Detection** - Automatic speech detection (no button pressing)
- **Noise Cancellation** - Optimized for child speech patterns

## 📁 Project Structure

```
KidSafe-Alphabet-Tutor/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints (auth, health, memory, vision)
│   │   ├── services/          # Business logic services
│   │   │   ├── agent_service.py      # Performance optimization
│   │   │   ├── auth_service.py       # Authentication & security
│   │   │   ├── curriculum_service.py # A-Z lesson progression
│   │   │   ├── memory_service.py     # 3-turn memory system
│   │   │   ├── phoneme_service.py    # Speech processing & phonics
│   │   │   ├── safety_service.py     # COPPA compliance
│   │   │   └── vision_service.py     # Computer vision
│   │   ├── config.py          # Configuration management
│   │   ├── livekit_voice_agent.py    # LiveKit voice agent
│   │   ├── main_livekit.py    # FastAPI app with token generation
│   │   ├── lessons.json       # Curriculum data
│   │   └── lessons_complete.json     # Extended curriculum
│   ├── run_livekit_agent.py   # Agent execution script
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml        # Project configuration
│   └── env.example           # Environment variables template
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Avatar/        # Avatar system (animations, expressions)
│   │   │   ├── Camera/        # Camera panel (vision integration)
│   │   │   ├── Lesson/        # Lesson interface (curriculum display)
│   │   │   ├── Memory/        # Memory panel (conversation history)
│   │   │   ├── Progress/      # Progress tracking (achievements)
│   │   │   ├── Settings/      # Settings & parental controls
│   │   │   └── LiveKitRoom.js # Real-time voice communication
│   │   ├── App.js            # Main application component
│   │   └── index.js          # React entry point
│   ├── public/index.html     # HTML template
│   └── package.json          # Node.js dependencies
└── project_requirements/     # Documentation and requirements
```

## 🛠️ Technology Stack

### Backend Technologies
- **FastAPI** - Modern Python web framework
- **LiveKit** - Real-time communication platform
- **OpenAI Whisper** - Speech-to-text for child voices
- **GPT-4** - Large language model for conversational AI
- **OpenAI TTS** - Text-to-speech synthesis
- **Python 3.11+** - Programming language
- **UV** - Fast Python package manager

### Frontend Technologies
- **React 18** - JavaScript UI framework
- **LiveKit React SDK** - Real-time communication client
- **Tailwind CSS** - Utility-first CSS framework
- **Node.js** - JavaScript runtime
- **npm** - Package manager

### Infrastructure & Tools
- **LiveKit Cloud** - Hosted real-time infrastructure
- **Git** - Version control with feature branch workflow
- **Environment Variables** - Secure configuration management

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **LiveKit Cloud Account** (for real-time communication)
- **OpenAI API Key** (for AI services)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   # Using UV (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys:
   # - OPENAI_API_KEY
   # - LIVEKIT_URL
   # - LIVEKIT_API_KEY
   # - LIVEKIT_API_SECRET
   ```

4. **Run the FastAPI server:**
   ```bash
   # Start token generation server
   python app/main_livekit.py
   
   # In another terminal, start the LiveKit agent
   python run_livekit_agent.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3001`

## 🎮 How to Use

1. **Start both backend and frontend servers**
2. **Open the frontend in your browser** at `http://localhost:3001`
3. **Allow microphone permissions** when prompted
4. **Start speaking** - The AI tutor will automatically detect your voice
5. **Practice letters** - The tutor will guide you through A-Z progression
6. **Get feedback** - Receive pronunciation coaching and encouragement

## 🔧 Development Workflow

### Branch Structure
The project uses a feature branch workflow with focused branches:

- **Core Infrastructure**: `backend-core`, `frontend-core`, `livekit-integration`
- **UI Components**: `ui-avatar-system`, `ui-camera-panel`, `ui-lesson-interface`, etc.
- **Services**: `speech-processing`, `vision-recognition`, `curriculum-engine`, etc.

### Development Order
1. Backend core infrastructure
2. LiveKit integration
3. Frontend core
4. UI components
5. Advanced services

## 🛡️ Safety & Compliance

- **COPPA Compliant** - Designed for children under 13
- **No Data Storage** - Real-time processing without persistent data
- **Parental Controls** - Settings access requires parental verification
- **Content Moderation** - AI responses filtered for child-appropriate content
- **Secure Communication** - Token-based authentication for all sessions

## 📊 Performance

- **Sub-1.2s Response Time** - Optimized for real-time interaction
- **Voice Activity Detection** - Automatic speech detection
- **Noise Cancellation** - Optimized for child speech patterns
- **Efficient Streaming** - LiveKit Cloud infrastructure

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make focused commits with descriptive messages
3. Create a pull request with detailed description
4. Ensure all tests pass and safety requirements are met

## 📄 License

This project is designed for educational purposes with child safety as the primary concern.