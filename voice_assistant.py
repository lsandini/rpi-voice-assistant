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
                            os.path.join(os.path.dirname(__file__), 'google-service-account.json'))

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
                # Only print non-empty status messages
                if str(status).strip():
                    print(f"Audio input status: {status}")
                return
            
            # Convert indata to bytes
            data_bytes = indata.astype(np.int16).tobytes()
            
            # Use a try-except to handle potential processing errors
            try:
                if rec.AcceptWaveform(data_bytes):
                    result = json.loads(rec.Result())
                    if result.get('text', '').strip():
                        self.text_queue.put(result['text'])
            except Exception as e:
                print(f"Error processing audio: {e}")

        # Open microphone stream with a larger buffer
        with sd.InputStream(
            samplerate=self.sample_rate, 
            device=self.device,
            dtype='int16', 
            channels=1, 
            callback=audio_callback,
            blocksize=2048  # Increase buffer size
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

    # ... (rest of the script remains the same)