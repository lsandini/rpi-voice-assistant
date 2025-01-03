#!/bin/bash

# Exit on error
set -e

echo "Installing RPI Voice Assistant dependencies..."

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    sox \
    libsox-fmt-all \
    libatlas-base-dev \
    libasound2-dev \
    alsa-utils

# Determine script and project directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create Python virtual environment
echo "Setting up Python virtual environment..."
cd "$PROJECT_ROOT"
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install \
    vosk \
    sounddevice \
    numpy \
    google-cloud-texttospeech \
    python-dotenv 

# Create necessary directories
echo "Creating project directories..."
mkdir -p "$PROJECT_ROOT/models/"{vosk,tts}
mkdir -p "$PROJECT_ROOT/config"

# Download Vosk model
echo "Downloading Vosk model..."
cd "$PROJECT_ROOT/models/vosk"
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip

# Return to original directory
cd "$PROJECT_ROOT"

# Create Google TTS Python script
echo "Creating Google TTS script..."
cat > "$PROJECT_ROOT/tts.py" << 'EOF'
from google.cloud import texttospeech
import os

def text_to_speech(text, output_file='/tmp/google_tts_output.wav', language_code='en-US'):
    # Set the path to your JSON key file
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), 'google-service-account.json')

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Write the response to the output file
    with open(output_file, 'wb') as out:
        out.write(response.audio_content)
        print(f'Audio content written to file {output_file}')

    # Play the audio file
    os.system(f'aplay {output_file}')

# Example usage
if __name__ == "__main__":
    text_to_speech("Hello, this is a test of Google Text-to-Speech")
EOF

# Instruction for service account key
echo "IMPORTANT: Please place your Google Cloud service account JSON key file at:"
echo "$PROJECT_ROOT/google-service-account.json"

echo "Installation complete!"
echo "Please edit config/custom.json with your API keys and preferences"
echo "Ensure you've placed the Google Cloud service account key at google-service-account.json"
echo "Run 'npm start' to launch the voice assistant"