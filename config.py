# Audio capture
SAMPLE_RATE = 16000
CHANNELS = 1
DEVICE_NAME = "BlackHole 2ch"
CHUNK_DURATION = 5.0       # seconds per chunk sent to Whisper
OVERLAP_DURATION = 0.5     # seconds of overlap between chunks
SILENCE_THRESHOLD = 0.01   # RMS below this = silence, skip processing

# Whisper
MODEL_SIZE = "medium"
DEVICE = "mps"             # "mps" for Apple Silicon, "cpu" fallback, "cuda" for NVIDIA
LANGUAGE = "ja"

# Display
MAX_DISPLAY_LINES = 20
