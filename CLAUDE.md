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

### Hardware Testing
```bash
# Test camera indices
uv run checkcamindx.py

# Test API connectivity
uv run fetchDataFromAPI.py
```

## Architecture Overview

### Core Components

1. **main.py** - Application entry point with multi-threaded execution:
   - Face detection loop (camera monitoring)
   - Speech recognition thread (microphone listening)
   - TTS processing thread (speech output)
   - Auto-suggestion system
   - CPU optimization and process priority management

2. **Face Recognition System** (`insightfacePyWith.py`):
   - Real-time face detection using InsightFace
   - Gender and age estimation
   - User presence tracking and greeting logic
   - Distance calculation for user presence detection

3. **Speech Processing**:
   - `listener.py` - Speech recognition using DashScope ASR
   - `speak.py` - Text-to-speech with streaming audio synthesis
   - `listenSpeakLLM.py` - Combined speech processing workflow with LLM integration

4. **Product Management**:
   - `fetchDataFromAPI.py` - External API client for product data (configurable endpoint)
   - `productInfoAPI/` - Local Flask server for product/service configuration
   - RESTful API with CRUD operations for managing assistant configurations

5. **Utilities** (`utils/`):
   - `chat.py` - System prompts and conversation history management
   - `greetings.py` - Gender-based greeting messages
   - `suggestion.py` - Auto-suggestion system
   - `RealtimeMp3Player.py` - Streaming audio playback
   - `echocheck.py` - Echo detection to prevent processing system audio

### Key Configuration Files

- **pyproject.toml** - Project dependencies and metadata with uv package manager
- **.env** - API keys (DashScope) and configuration variables
- **productInfoAPI/data.json** - Product/service data for the assistant
- **assistant_info.sql** - Database schema for PostgreSQL backend integration
- **coffeeassitant.service** - Systemd service configuration for production deployment

## Application Flow

1. **Initialization**: Load face detection models, API keys, and product data from external API
2. **Multi-threaded Execution**: Start parallel threads for camera monitoring, speech processing, and auto-suggestions
3. **User Detection**: Face detection triggers gender-based greetings (dynamically loaded from API configuration)
4. **Interactive Loop**: Process voice commands with echo detection, provide responses using LLM, and manage conversation context
5. **Speech Management**: System pauses speech recognition when speaking to prevent feedback loops
6. **Absence Detection**: Monitor for user departure and reset system state with configurable thresholds

## Threading Architecture

### Core Threads
- **Main Thread**: Application lifecycle management and coordination
- **Face Detection Thread**: Real-time computer vision processing with InsightFace
- **Speech Recognition Thread**: Continuous microphone monitoring with automatic pause/resume
- **TTS Processing Thread**: Text-to-speech synthesis with streaming audio playback
- **Auto-suggestion Thread**: Proactive user engagement when users are present but not actively engaged

### Thread Synchronization
- Uses `threading.Lock()` and `threading.Event()` for coordination
- `NOW_SPEAKING` lock prevents speech recognition during TTS playback
- `STOP_EVENT` for graceful shutdown coordination
- `USER_ABSENT` flag for managing user presence state
- Queue-based communication between threads (`userQueryQueue`)

## Important Development Notes

### Hardware Dependencies
- **Camera**: OpenCV-compatible camera for face detection (configurable via `--camid`)
- **Microphone**: PyAudio-compatible microphone for speech input
- **Speakers**: Audio output for TTS responses

### API Requirements
- **DashScope API Key**: Required for speech recognition and text-to-speech (stored as `DASHSCOPEAPIKEY` in .env)
- **External Product API**: Optional for dynamic product data (configurable endpoint in `fetchDataFromAPI.py`)

### Configuration Variables (.env)
- `DASHSCOPEAPIKEY` - Alibaba Cloud DashScope API key (note: different variable name than typical)
- Camera and audio device indices may need adjustment per deployment environment
- External API endpoint in `fetchDataFromAPI.py` may need configuration for different deployment environments

### System Prompt Configuration
- System prompts are dynamically loaded from API or local configuration
- Current configuration supports blind dating event organizer context (in Chinese)
- Includes filtering rules to prevent responses to irrelevant conversations
- Configurable through `utils/chat.py` and external API

### Performance Optimization
- CPU affinity optimization available via `cpu_optimizer.py`
- Process priority management for real-time processing
- Configurable absence thresholds and detection intervals
- Frame capture debugging (saved to `frames/` directory)

### Error Handling Patterns
- Robust exception handling for hardware failures (camera, microphone)
- API timeout and retry mechanisms for DashScope services
- Graceful degradation when face detection or speech services fail
- Echo detection prevents processing of system audio feedback

### Testing and Quality Assurance
- No formal testing framework is currently implemented
- Manual testing recommended for hardware components
- Use `checkcamindx.py` to test camera availability and indices
- Use `fetchDataFromAPI.py` to test external API connectivity
- Monitor console logs for debugging information

### Deployment Considerations
- Supports headless mode for production deployments without display
- Systemd service configuration included (`coffeeassitant.service`)
- Proper camera and microphone permissions required
- Configure appropriate device indices for target hardware
- Set up external API endpoints or use local Flask server
- Consider CPU optimization for resource-constrained environments

### Code Organization Patterns
- **Modular Design**: Separate modules for distinct functionality (speech, vision, chat)
- **Import Management**: All utilities imported from `utils/` directory
- **Threading Safety**: Extensive use of locks and events for thread coordination
- **Error Handling**: Try-catch blocks with meaningful error messages
- **Logging**: Console-based logging throughout the application for debugging

### Database Integration
- PostgreSQL schema available (`assistant_info.sql`)
- Support for storing multiple assistant configurations
- Array fields for suggestions and greetings
- Timestamp tracking for configuration changes