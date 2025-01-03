import vosk
import sounddevice as sd
import json
import numpy as np
from google.cloud import texttospeech
import os
import queue
import threading
import time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables at the start of the script
load_dotenv()

class VoiceAssistant:
    def __init__(self, model_path, sample_rate=16000, device=None):
        # Get credentials path from environment variable or use project root
        key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 
                            os.path.join(os.path.dirname(__file__), 'google-service-accounts.json'))

        # Verify the key file exists
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Google Cloud service account key not found at {key_path}")

        # Set the credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

        # Initialize Vosk model
        vosk.SetLogLevel(-1)
        self.model = vosk.Model(model_path)
        self.sample_rate = sample_rate
        self.device = device

        # Queue for recognized text
        self.text_queue = queue.Queue()

        # Google TTS client
        self.tts_client = texttospeech.TextToSpeechClient()

        # Event to stop the assistant
        self.stop_event = threading.Event()

    def recognize_speech(self):
        # Speech recognition using Vosk
        rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            # Convert indata to bytes
            data_bytes = indata.astype(np.int16).tobytes()
            if rec.AcceptWaveform(data_bytes):
                result = json.loads(rec.Result())
                if result.get('text', '').strip():
                    self.text_queue.put(result['text'])

        # Open microphone stream
        with sd.InputStream(
            samplerate=self.sample_rate, 
            device=self.device,
            dtype='int16', 
            channels=1, 
            callback=audio_callback
        ):
            print("Listening... Speak now.")
            
            # Process recognized text in a separate thread
            def process_text():
                while not self.stop_event.is_set():
                    try:
                        text = self.text_queue.get(timeout=1)
                        if text:
                            print(f"Recognized: {text}")
                            self.process_command(text)
                    except queue.Empty:
                        continue

            # Start text processing thread
            text_thread = threading.Thread(target=process_text, daemon=True)
            text_thread.start()

            # Keep the script running
            try:
                while not self.stop_event.is_set():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping voice assistant...")
                self.stop_event.set()

    def text_to_speech(self, text, output_file='/tmp/tts_output.wav', language_code='en-US'):
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
        response = self.tts_client.synthesize_speech(
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

    def process_command(self, text):
        # Simple command processing
        text = text.lower().strip()
        
        # Example commands
        if "hello" in text:
            self.text_to_speech("Hello! How can I help you?")
        elif "time" in text:
            current_time = datetime.now().strftime("%I:%M %p")
            self.text_to_speech(f"The current time is {current_time}")
        elif "goodbye" in text or "bye" in text:
            self.text_to_speech("Goodbye! Have a great day.")
            self.stop_event.set()
        else:
            # Echo back the recognized text
            self.text_to_speech(f"You said: {text}")

def main():
    # Path to Vosk model (adjust to your actual model path)
    vosk_model_path = "/home/lorenzo/rpi-voice-assistant/models/vosk/vosk-model-small-en-us-0.15"
    
    # Initialize voice assistant
    assistant = VoiceAssistant(vosk_model_path)
    
    # Start listening
    assistant.recognize_speech()

if __name__ == "__main__":
    main()