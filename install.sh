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
    libasound2-dev

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Create Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install \
    vosk \
    sounddevice \
    numpy

# Install Piper TTS
echo "Installing Piper TTS..."
wget https://github.com/rhasspy/piper/releases/download/latest/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper /usr/local/bin/
rm piper_amd64.tar.gz

# Create necessary directories
echo "Creating project directories..."
mkdir -p models/{vosk,piper}
mkdir -p config

# Download Vosk model
echo "Downloading Vosk model..."
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/vosk/
rm vosk-model-small-en-us-0.15.zip

# Download Piper voice model
echo "Downloading Piper voice model..."
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx -O models/piper/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.json -O models/piper/en_US-lessac-medium.json

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Configure audio
echo "Configuring audio..."
sudo cp config/asound.conf /etc/asound.conf

# Set up service (optional)
if [ "$1" == "--service" ]; then
    echo "Setting up systemd service..."
    sudo cp config/voice-assistant.service /etc/systemd/system/
    sudo systemctl enable voice-assistant
    sudo systemctl start voice-assistant
fi

echo "Installation complete!"
echo "Please edit config/custom.json with your API keys and preferences"
echo "Run 'npm start' to launch the voice assistant"
