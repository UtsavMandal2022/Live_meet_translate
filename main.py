import argparse
import queue
import sys
import threading
import logging

import config
from utils import setup_logging
from audio_capture import AudioCapture, list_devices
from processor import Processor, load_model
from display import Display

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Live Japanese → English translation for Google Meet using Whisper"
    )
    parser.add_argument(
        "--model", default=config.MODEL_SIZE,
        choices=["tiny", "base", "small", "medium", "large", "large-v3"],
        help=f"Whisper model size (default: {config.MODEL_SIZE})"
    )
    parser.add_argument(
        "--device", default=config.DEVICE,
        choices=["mps", "cpu", "cuda"],
        help=f"Compute device (default: {config.DEVICE})"
    )
    parser.add_argument(
        "--chunk-duration", type=float, default=config.CHUNK_DURATION,
        help=f"Audio chunk duration in seconds (default: {config.CHUNK_DURATION})"
    )
    parser.add_argument(
        "--audio-device", default=config.DEVICE_NAME,
        help=f"Audio input device name (default: {config.DEVICE_NAME})"
    )
    parser.add_argument(
        "--list-devices", action="store_true",
        help="List available audio input devices and exit"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable debug logging"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(verbose=args.verbose)

    if args.list_devices:
        list_devices()
        sys.exit(0)

    # Load Whisper model
    model = load_model(model_size=args.model, device=args.device)

    # Shared state
    audio_queue = queue.Queue(maxsize=10)
    result_queue = queue.Queue(maxsize=50)
    stop_event = threading.Event()

    # Create components
    capture = AudioCapture(
        audio_queue=audio_queue,
        stop_event=stop_event,
        device_name=args.audio_device,
        chunk_duration=args.chunk_duration,
    )
    processor = Processor(
        model=model,
        audio_queue=audio_queue,
        result_queue=result_queue,
        stop_event=stop_event,
    )
    display = Display(
        result_queue=result_queue,
        stop_event=stop_event,
        model_size=args.model,
        chunk_duration=args.chunk_duration,
    )

    # Start threads
    threads = [
        threading.Thread(target=capture.run, name="audio-capture", daemon=True),
        threading.Thread(target=processor.run, name="processor", daemon=True),
        threading.Thread(target=display.run, name="display", daemon=True),
    ]

    logger.info("Starting live translation... Press Ctrl+C to stop.")
    for t in threads:
        t.start()

    try:
        # Wait for Ctrl+C
        while True:
            for t in threads:
                t.join(timeout=0.5)
                if not t.is_alive() and not stop_event.is_set():
                    logger.error(f"Thread '{t.name}' died unexpectedly")
                    stop_event.set()
                    sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nStopping...")
        stop_event.set()
        for t in threads:
            t.join(timeout=3)
        logger.info("Done.")


if __name__ == "__main__":
    main()
