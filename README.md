# CoffeV4 - AI-Powered Interactive Assistant

An AI-powered interactive assistant/kiosk application that combines computer vision, speech recognition, and text-to-speech capabilities for real-world deployment scenarios like coffee shops or service kiosks.

## Features

- **Real-time Face Detection**: Uses InsightFace for gender and age detection
- **Speech Recognition**: Alibaba DashScope API for natural language processing
- **Text-to-Speech**: Streaming audio synthesis for natural conversations
- **Multi-threaded Architecture**: Concurrent processing for smooth user experience
- **Echo Detection**: Prevents processing of system audio feedback
- **Auto-suggestions**: Proactive engagement when users are present
- **Configurable Products/Services**: Dynamic configuration via API or local data

## Technology Stack

- **Python 3.13+** with `uv` package manager
- **Computer Vision**: OpenCV, InsightFace (ONNX Runtime)
- **Speech Processing**: Alibaba DashScope API
- **Audio**: PyAudio for real-time microphone input
- **Web Framework**: Flask API for product/service management
- **Threading**: Multi-threaded execution for real-time performance

## Quick Start

### Prerequisites

- Python 3.13 or higher
- Compatible camera (webcam)
- Microphone and speakers
- DashScope API key from Alibaba Cloud

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd coffev4
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Create a `.env` file with your API key:
```bash
DASHSCOPEAPIKEY=your_dashscope_api_key_here
```

### Running the Application

```bash
# Main application with GUI
uv run main.py

# Headless mode (no camera display)
uv run main.py --headless

# Specify camera index
uv run main.py --camid 0

# Run product info API server (optional)
uv run productInfoAPI/main.py
```

## Project Structure

```
coffev4/
├── main.py                     # Application entry point
├── insightfacePyWith.py       # Face detection and analysis
├── listener.py                # Speech recognition
├── speak.py                   # Text-to-speech synthesis
├── listenSpeakLLM.py         # Combined speech processing
├── fetchDataFromAPI.py       # External API client
├── checkcamindx.py           # Camera testing utility
├── cpu_optimizer.py          # Performance optimization
├── productInfoAPI/           # Local API server
│   ├── main.py              # Flask server
│   └── data.json            # Product/service configuration
├── utils/                   # Utility modules
│   ├── chat.py             # System prompts and conversation
│   ├── greetings.py        # Gender-based greetings
│   ├── suggestion.py       # Auto-suggestion system
│   ├── RealtimeMp3Player.py # Streaming audio playback
│   └── echocheck.py        # Echo detection
├── frames/                 # Camera frame captures (ignored in git)
├── pyproject.toml         # Project dependencies
└── .env                   # API keys (create this file)
```

## Configuration

### Environment Variables (.env)
- `DASHSCOPEAPIKEY`: Alibaba Cloud DashScope API key for speech services

### Product/Service Configuration
Edit `productInfoAPI/data.json` to configure:
- System prompts for different contexts (coffee shop, events, etc.)
- Available products/services
- Greeting messages
- Auto-suggestions

### Hardware Configuration
- Camera index can be specified with `--camid` parameter
- Audio device configuration may need adjustment in `listener.py` and `speak.py`

## Usage

1. **Start the application**: The system initializes face detection, speech recognition, and TTS services
2. **User Detection**: When a face is detected, the system provides a gender-appropriate greeting
3. **Voice Interaction**: Users can speak naturally; the system processes queries and responds
4. **Auto-suggestions**: If users are present but not actively engaging, the system offers helpful suggestions
5. **Absence Detection**: When users leave, the system resets and waits for the next interaction

## API Integration

The application can fetch product/service data from external APIs:
- Configure endpoint in `fetchDataFromAPI.py`
- Or use the local Flask server in `productInfoAPI/`
- Data structure supports multiple contexts (coffee shop, events, etc.)

## Testing

### Hardware Testing
```bash
# Test camera availability
uv run checkcamindx.py

# Test API connectivity
uv run fetchDataFromAPI.py
```

### Manual Testing
- Verify camera feed displays correctly
- Test microphone input and speaker output
- Confirm face detection triggers appropriate greetings
- Test speech recognition with various voice commands

## Deployment

### Production Considerations
- Use `--headless` mode for deployments without displays
- Ensure proper camera and microphone permissions
- Configure appropriate device indices for target hardware
- Set up external API endpoints or use local Flask server
- Consider systemd service configuration (see `coffeeassitant.service`)

### Performance Optimization
- CPU optimization features available via `cpu_optimizer.py`
- Threading architecture designed for real-time performance
- Configurable distance thresholds and absence timers

## Architecture Details

### Threading Model
- **Main Thread**: Application lifecycle management
- **Face Detection Thread**: Real-time computer vision processing
- **Speech Recognition Thread**: Continuous microphone monitoring
- **TTS Processing Thread**: Text-to-speech synthesis and playback
- **Auto-suggestion Thread**: Proactive user engagement

### Thread Synchronization
- Uses locks and events to coordinate between threads
- Automatic pause/resume of speech recognition during TTS playback
- User presence detection affects system behavior

### Error Handling
- Robust error handling for hardware failures
- API timeout and retry mechanisms
- Graceful degradation when components fail

## Dependencies

Core dependencies (see `pyproject.toml` for full list):
- `insightface>=0.7.3` - Face detection and analysis
- `opencv-python>=4.11.0.86` - Computer vision
- `dashscope>=1.23.5` - Alibaba Cloud speech services
- `pyaudio>=0.2.14` - Audio input/output
- `onnxruntime>=1.22.0` - ML model inference
- `aiohttp>=3.12.13` - HTTP client for API calls
- `psutil>=6.1.0` - System monitoring

## Troubleshooting

### Common Issues
1. **Camera not detected**: Check camera index with `checkcamindx.py`
2. **Audio issues**: Verify microphone/speaker permissions and device indices
3. **API errors**: Confirm DashScope API key is valid and has sufficient quota
4. **Face detection fails**: Ensure adequate lighting and camera positioning

### Logging
- Console-based logging throughout the application
- Monitor logs for hardware and API issues
- Frame captures saved to `frames/` directory for debugging

## Contributing

1. Follow existing code conventions and patterns
2. Test hardware components before submitting changes
3. Update documentation for new features
4. Ensure thread safety in concurrent operations

## License

[Specify your license here]

## Support

For issues and questions:
- Check the troubleshooting section above
- Review console logs for error details
- Test individual components (camera, microphone, API connectivity)