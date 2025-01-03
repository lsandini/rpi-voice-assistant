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

# Determine architecture
if [ "$1" = "--arm64" ]; then
    PIPER_ARCH="arm64"
    echo "Using ARM64 architecture"
elif [ "$1" = "--amd64" ]; then
    PIPER_ARCH="amd64"
    echo "Using AMD64 architecture"
else
    ARCH=$(uname -m)
    echo "Detected architecture: $ARCH"
    case $ARCH in
        aarch64|arm64)
            PIPER_ARCH="arm64"
            ;;
        armv7l|armv6l)
            PIPER_ARCH="armv7"
            ;;
        x86_64)
            PIPER_ARCH="amd64"
            ;;
        *)
            echo "Unsupported architecture: $ARCH"
            echo "Please specify architecture manually using --arm64 or --amd64"
            exit 1
            ;;
    esac
fi

echo "Selected Piper architecture: $PIPER_ARCH"
PIPER_VERSION="1.2.0"
PIPER_FILE="piper_${PIPER_ARCH}.tar.gz"
DOWNLOAD_URL="https://github.com/rhasspy/piper/releases/download/v${PIPER_VERSION}/${PIPER_FILE}"

echo "Downloading Piper from: $DOWNLOAD_URL"
wget --content-disposition "$DOWNLOAD_URL"

echo "Extracting $PIPER_FILE..."
tar -xvf "$PIPER_FILE"

echo "Installing Piper..."
# First, clean up any existing installation
sudo rm -rf /usr/local/bin/piper
sudo rm -rf /usr/local/bin/espeak-ng-data

# Now copy everything
sudo cp -r piper/* /usr/local/bin/

echo "Cleaning up..."
rm -rf piper
rm "$PIPER_FILE"

# Create necessary directories
echo "Creating project directories..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
mkdir -p "$PROJECT_ROOT/models/"{vosk,piper}
mkdir -p "$PROJECT_ROOT/config"

# Download Vosk model
echo "Downloading Vosk model..."
cd "$PROJECT_ROOT/models/vosk"
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip -o vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip
cd "$SCRIPT_DIR"

# Download Piper voice model
echo "Downloading Piper voice model..."
cd "$PROJECT_ROOT/models/piper"
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx -O en_US-lessac-medium.onnx

# Create Piper configuration
echo "Creating Piper configuration..."
cat > en_US-lessac-medium.json << 'EOF'
{
    "espeak": {
        "voice": "en-us"
    },
    "length_scale": 1.0,
    "noise_scale": 0.667,
    "noise_w": 0.8,
    "sample_rate": 22050,
    "speaker_id": 0
}
EOF

# Return to script directory
cd "$SCRIPT_DIR"

# Test Piper
echo "Testing Piper installation..."
if command -v piper &> /dev/null; then
    echo "Piper found. Testing synthesis..."
    echo "Using config at: $PROJECT_ROOT/models/piper/en_US-lessac-medium.json"
    echo "Config contents:"
    cat "$PROJECT_ROOT/models/piper/en_US-lessac-medium.json"
    echo "Running test..."
    if echo "Test" | piper \
        --model "$PROJECT_ROOT/models/piper/en_US-lessac-medium.onnx" \
        --config "$PROJECT_ROOT/models/piper/en_US-lessac-medium.json" \
        --output_raw \
        --debug 2>&1; then
        echo "Piper synthesis test successful!"
    else
        echo "Warning: Piper synthesis test failed. Try running this command manually:"
        echo "echo 'Test' | piper --model $PROJECT_ROOT/models/piper/en_US-lessac-medium.onnx --config $PROJECT_ROOT/models/piper/en_US-lessac-medium.json --output_raw"
    fi
else
    echo "Warning: Piper not found in PATH."
fi

echo "Installation complete!"
echo "Please edit config/custom.json with your API keys and preferences"
echo "Run 'npm start' to launch the voice assistant"