import threading
import queue
import time
from collections import deque

import numpy as np
import sounddevice as sd

import config


class AudioCapture:
    def __init__(self, audio_queue: queue.Queue, stop_event: threading.Event,
                 device_name: str = None, chunk_duration: float = None,
                 overlap_duration: float = None):
        self.audio_queue = audio_queue
        self.stop_event = stop_event
        self.device_name = device_name or config.DEVICE_NAME
        self.chunk_duration = chunk_duration or config.CHUNK_DURATION
        self.overlap_duration = overlap_duration or config.OVERLAP_DURATION
        self.sample_rate = config.SAMPLE_RATE
        self.channels = config.CHANNELS

        self.chunk_samples = int(self.chunk_duration * self.sample_rate)
        self.overlap_samples = int(self.overlap_duration * self.sample_rate)

        self._buffer = deque(maxlen=self.chunk_samples + self.overlap_samples)
        self._lock = threading.Lock()

    def _find_device(self) -> int:
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if self.device_name.lower() in dev["name"].lower() and dev["max_input_channels"] > 0:
                return i
        raise RuntimeError(
            f"Audio device '{self.device_name}' not found. "
            f"Run with --list-devices to see available devices."
        )

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass  # dropped frames etc — not critical
        with self._lock:
            self._buffer.extend(indata[:, 0].tolist())

    def run(self):
        device_id = self._find_device()
        stream = sd.InputStream(
            device=device_id,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._audio_callback,
            blocksize=1024,
        )

        with stream:
            while not self.stop_event.is_set():
                time.sleep(0.1)
                with self._lock:
                    if len(self._buffer) >= self.chunk_samples:
                        # Extract chunk
                        chunk = np.array(list(self._buffer), dtype=np.float32)[:self.chunk_samples]
                        # Keep overlap for next chunk
                        to_remove = self.chunk_samples - self.overlap_samples
                        for _ in range(to_remove):
                            self._buffer.popleft()
                        # Check if silence
                        rms = np.sqrt(np.mean(chunk ** 2))
                        if rms < config.SILENCE_THRESHOLD:
                            continue
                        self.audio_queue.put((time.time(), chunk))


def list_devices():
    devices = sd.query_devices()
    print("\nAvailable audio input devices:\n")
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            marker = " <--" if config.DEVICE_NAME.lower() in dev["name"].lower() else ""
            print(f"  [{i}] {dev['name']} ({dev['max_input_channels']}ch, {int(dev['default_samplerate'])}Hz){marker}")
    print()
