import threading
import queue
import time
import logging

import whisper
import torch

import config

logger = logging.getLogger(__name__)


def load_model(model_size: str = None, device: str = None):
    model_size = model_size or config.MODEL_SIZE
    device = device or config.DEVICE

    if device == "mps" and not torch.backends.mps.is_available():
        logger.warning("MPS not available, falling back to CPU")
        device = "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA not available, falling back to CPU")
        device = "cpu"

    logger.info(f"Loading Whisper model '{model_size}' on {device}...")
    model = whisper.load_model(model_size, device=device)
    logger.info("Model loaded.")
    return model


class Processor:
    def __init__(self, model, audio_queue: queue.Queue, result_queue: queue.Queue,
                 stop_event: threading.Event):
        self.model = model
        self.audio_queue = audio_queue
        self.result_queue = result_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                timestamp, audio = self.audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            start = time.time()

            try:
                # Transcribe in Japanese
                ja_result = self.model.transcribe(
                    audio,
                    language=config.LANGUAGE,
                    task="transcribe",
                    fp16=False,
                )
                japanese = ja_result["text"].strip()

                # Translate to English
                en_result = self.model.transcribe(
                    audio,
                    language=config.LANGUAGE,
                    task="translate",
                    fp16=False,
                )
                english = en_result["text"].strip()
            except Exception as e:
                logger.error(f"Whisper error: {e}")
                continue

            process_time = time.time() - start

            if japanese or english:
                self.result_queue.put({
                    "timestamp": timestamp,
                    "japanese": japanese,
                    "english": english,
                    "process_time": process_time,
                })
