from google.cloud import texttospeech
import os
import threading
import time
from dotenv import load_dotenv
from datetime import datetime
import logging
from stt import SpeechToText

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/tmp/voice_assistant.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

class VoiceAssistant:
    def __init__(self, model_path, sample_rate=16000, device=None):
        logging.info("Initializing Voice Assistant")
        
        try:
            # Get credentials path from environment variable or use project root
            key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 
                                os.path.join(os.path.dirname(__file__), 'google-service-account.json'))

            # Verify the key file exists
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"Google Cloud service account key not found at {key_path}")

            # Set the credentials
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

            # Initialize STT engine
            self.stt_engine = SpeechToText(model_path, sample_rate, device)

            # Google TTS client
            self.tts_client = texttospeech.TextToSpeechClient()

            # Event to stop the assistant
            self.stop_event = threading.Event()

            logging.info("Voice Assistant initialized successfully")
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            raise

    def start(self):
        """Start the voice assistant."""
        logging.info("Starting voice assistant")
        
        # Start speech recognition with command processing callback
        self.stt_engine.start_recognition(callback_fn=self.process_command)
        
        # Keep the assistant running
        while not self.stop_event.is_set():
            time.sleep(1)

    def stop(self):
        """Stop the voice assistant."""
        self.stop_event.set()
        self.stt_engine.stop_recognition()

    def text_to_speech(self, text, output_file='/tmp/tts_output.wav', language_code='en-US'):
        """Convert text to speech and play it."""
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )

        with open(output_file, 'wb') as out:
            out.write(response.audio_content)
            print(f'Audio content written to file {output_file}')

        os.system(f'aplay {output_file}')

    def process_command(self, text):
        """Process recognized text commands."""
        text = text.lower().strip()
        
        # Prevent repeated processing of the same text
        if not hasattr(self, '_last_processed_text'):
            self._last_processed_text = None

        if text == self._last_processed_text:
            return

        self._last_processed_text = text
        
        # Handle commands
        if "hello" in text:
            self.text_to_speech("Hello! How can I help you?")
        elif "time" in text:
            current_time = datetime.now().strftime("%I:%M %p")
            self.text_to_speech(f"The current time is {current_time}")
        elif "goodbye" in text or "bye" in text:
            self.text_to_speech("Goodbye! Have a great day.")
            self.stop()
        else:
            self.text_to_speech(f"You said: {text}")

def main():
    try:
        # Path to Vosk model
        vosk_model_path = "/home/lorenzo/rpi-voice-assistant/models/vosk/vosk-model-small-en-us-0.15"
        
        # Initialize and start voice assistant
        assistant = VoiceAssistant(vosk_model_path)
        assistant.start()
    
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        raise

if __name__ == "__main__":
    main()