# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered interactive assistant/kiosk application built in Python that combines computer vision, speech recognition, and text-to-speech capabilities. The application is designed for real-world deployment scenarios like coffee shops or service kiosks, providing personalized interactions based on face detection and voice commands.

## Technology Stack

- **Python 3.13+** with `uv` package manager
- **Computer Vision:** OpenCV, InsightFace for face detection and gender/age analysis
- **Speech Processing:** Alibaba DashScope API for TTS and ASR
- **Audio:** PyAudio for real-time microphone input
- **Web Framework:** Flask API for product/service management
- **ML Inference:** ONNX Runtime for face recognition models

## Development Commands

### Running the Application
```bash
# Main application with GUI
uv run main.py

# Headless mode (no camera display)
uv run main.py --headless

# Specify camera index
uv run main.py --camid 0

# Run product info API server
uv run productInfoAPI/main.py
```

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Update dependencies
uv lock --upgrade
```

## Architecture Overview

### Core Components

1. **main.py** - Application entry point with multi-threaded execution:
   - Face detection loop (camera monitoring)
   - Speech recognition thread (microphone listening)
   - TTS processing thread (speech output)
   - Auto-suggestion system

2. **Face Recognition System** (`insightfacePyWith.py`):
   - Real-time face detection using InsightFace
   - Gender and age estimation
   - User presence tracking and greeting logic

3. **Speech Processing**:
   - `listener.py` - Speech recognition using DashScope ASR
   - `speak.py` - Text-to-speech with streaming audio
   - `listenSpeakLLM.py` - Combined speech processing workflow

4. **Product Management**:
   - `fetchDataFromAPI.py` - External API client for product data
   - `productInfoAPI/` - Local Flask server for product/service configuration

5. **Utilities** (`utils/`):
   - `chat.py` - System prompts and conversation history
   - `greetings.py` - Gender-based greeting messages
   - `suggestion.py` - Auto-suggestion system
   - `RealtimeMp3Player.py` - Streaming audio playback
   - `echocheck.py` - Echo detection to prevent processing system audio

### Key Configuration Files

- **pyproject.toml** - Project dependencies and metadata
- **.env** - API keys (DashScope) and configuration variables
- **productInfoAPI/data.json** - Product/service data for the assistant
- **assistant_info.sql** - Database schema information

## Application Flow

1. **Initialization**: Load face detection models, API keys, and product data from external API
2. **Multi-threaded Execution**: Start parallel threads for camera monitoring, speech processing, and auto-suggestions
3. **User Detection**: Face detection triggers gender-based greetings (dynamically loaded from API configuration)
4. **Interactive Loop**: Process voice commands with echo detection, provide responses using LLM, and manage conversation context
5. **Speech Management**: System pauses speech recognition when speaking to prevent feedback loops
6. **Absence Detection**: Monitor for user departure and reset system state with configurable thresholds

## Important Development Notes

### Hardware Dependencies
- **Camera**: OpenCV-compatible camera for face detection
- **Microphone**: PyAudio-compatible microphone for speech input
- **Speakers**: Audio output for TTS responses

### API Requirements
- **DashScope API Key**: Required for speech recognition and text-to-speech
- **External Product API**: Optional for dynamic product data (configurable endpoint)

### Configuration Variables (.env)
- `DASHSCOPEAPIKEY` - Alibaba Cloud DashScope API key (note: different variable name than typical)
- Camera and audio device indices may need adjustment per deployment environment
- External API endpoint in `fetchDataFromAPI.py` may need configuration for different deployment environments

### Testing and Quality Assurance
- No formal testing framework is currently implemented
- Manual testing recommended for hardware components (camera, microphone, speakers)
- Test camera indices with `checkcamindx.py` utility
- Test API connectivity with `fetchDataFromAPI.py` script

### Code Organization Patterns
- **Modular Design**: Separate modules for distinct functionality (speech, vision, chat)
- **Threading**: Extensive use of threading for real-time processing
- **Error Handling**: Robust error handling for hardware failures and API timeouts
- **Logging**: Console-based logging throughout the application

### Deployment Considerations
- Ensure proper camera and microphone permissions
- Configure appropriate device indices for target hardware
- Set up external API endpoints or use local Flask server
- Consider headless mode for production deployments without display
- The system supports dynamic configuration changes through API without restart
- Face detection distance thresholds and absence timers are configurable in main.py

### Key Threading Architecture
- **Main Thread**: Manages overall application lifecycle
- **Face Detection Thread**: Real-time face analysis with distance calculation and user presence tracking
- **Speech Recognition Thread**: Continuous microphone monitoring with automatic pause/resume based on system state
- **TTS Processing Thread**: Handles text-to-speech synthesis with streaming audio playback
- **Auto-suggestion Thread**: Provides periodic suggestions when user is present but not actively engaged
- **Thread Synchronization**: Uses locks and events to coordinate between speech recognition, TTS, and user presence detection