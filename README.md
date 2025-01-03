# rpi-voice-assistant# Raspberry Pi Voice Assistant

## Overview
This is an open-source voice assistant project designed to run on a Raspberry Pi, combining speech recognition, text-to-speech, and basic conversational capabilities.

## Features
- Real-time speech recognition using Vosk
- Google Cloud Text-to-Speech integration
- Voice command processing
- Logging and error handling

## Hardware Requirements
- Raspberry Pi (tested on Raspberry Pi 5)
- Microphone (recommended: Seeed 2-mic Voice Card)
- Speaker or audio output device

## Software Dependencies
- Python 3.9+
- Vosk speech recognition library
- Google Cloud Text-to-Speech
- python-dotenv
- sounddevice
- numpy

## Installation
1. Clone the repository
2. Run `scripts/install.sh --arm64` (or `--amd64` depending on your architecture)
3. Place your Google Cloud service account JSON file at the root of the project: `google-service-account.json`

## Configuration
- Customize voice settings in the configuration files
- Set up Google Cloud credentials
- Adjust model paths as needed

## Execution

### Starting the Voice Assistant
Run `bash start_assistant.sh` to activate the virtual environment and execute the application

## Current Capabilities
- Recognize spoken commands
- Respond to basic voice commands like:
  * Saying "hello" triggers a greeting
  * Asking for the time returns current time
  * Saying "goodbye" stops the assistant
- Real-time speech-to-text conversion
- Text-to-speech output using Google Cloud TTS

## Logging
- Detailed logs are maintained at `/tmp/voice_assistant.log`
- Provides debugging information and error tracking

## Future Roadmap
- OpenAI API integration
- Enhanced voice command recognition
- Expanded conversational abilities

## Troubleshooting
- Check `/tmp/voice_assistant.log` for detailed error information
- Ensure all dependencies are correctly installed
- Verify microphone and audio device configurations

## License
[Add your license information here]

## Contributors
[Add contributor information]