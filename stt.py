import vosk
import sounddevice as sd
import json
import numpy as np
import logging
import queue
import threading

class SpeechToText:
    def __init__(self, model_path, sample_rate=16000, device=None):
        """Initialize the Speech-to-Text engine.
        
        Args:
            model_path (str): Path to the Vosk model
            sample_rate (int): Audio sample rate
            device (int, optional): Audio input device ID
        """
        logging.info("Initializing Speech-to-Text")
        
        try:
            # Initialize Vosk model
            vosk.SetLogLevel(-1)
            self.model = vosk.Model(model_path)
            self.sample_rate = sample_rate
            self.device = device
            self.text_queue = queue.Queue()
            self.stop_event = threading.Event()
            
            logging.info("Speech-to-Text initialized successfully")
        except Exception as e:
            logging.error(f"STT initialization error: {e}")
            raise

    def start_recognition(self, callback_fn=None):
        """Start speech recognition with optional callback for recognized text.
        
        Args:
            callback_fn (callable, optional): Function to call with recognized text
        """
        logging.info("Starting speech recognition")
        
        rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        
        def audio_callback(indata, frames, time, status):
            if status:
                logging.warning(f"Audio input status: {status}")
                return
            
            data_bytes = indata.astype(np.int16).tobytes()
            
            try:
                if rec.AcceptWaveform(data_bytes):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    if text:
                        logging.info(f"Recognized speech: {text}")
                        self.text_queue.put(text)
                        if callback_fn:
                            callback_fn(text)
            except Exception as e:
                logging.error(f"Error processing audio: {e}")

        try:
            # Debug info
            logging.info(f"Available input devices: {sd.query_devices()}")
            logging.info(f"Using device: {self.device}")

            # Open microphone stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                device=self.device,
                dtype='int16',
                channels=1,
                callback=audio_callback
            ):
                logging.info("Microphone stream opened. Listening...")
                print("Listening... Speak now.")
                
                while not self.stop_event.is_set():
                    threading.Event().wait(1)

        except Exception as e:
            logging.error(f"Speech recognition error: {e}")
            raise

    def stop_recognition(self):
        """Stop the speech recognition."""
        self.stop_event.set()

    def get_recognized_text(self, timeout=1):
        """Get recognized text from the queue.
        
        Args:
            timeout (float): How long to wait for text
            
        Returns:
            str: Recognized text or None if queue is empty
        """
        try:
            return self.text_queue.get(timeout=timeout)
        except queue.Empty:
            return None

# Example usage
if __name__ == "__main__":
    # Simple test of the STT functionality
    def print_text(text):
        print(f"Recognized: {text}")

    model_path = "/path/to/vosk/model"
    stt = SpeechToText(model_path)
    stt.start_recognition(callback_fn=print_text)