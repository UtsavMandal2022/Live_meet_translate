# Live Meet Translate

Real-time Japanese-to-English translation for Google Meet calls, powered by OpenAI's [Whisper](https://github.com/openai/whisper) running locally on your machine.

Captures system audio via BlackHole, transcribes Japanese speech, and displays both the original Japanese text and English translation as live captions in your terminal.

## How it works

```
Google Meet audio → BlackHole (loopback) → Whisper → Live terminal captions
```

Audio is captured in 5-second chunks, each processed by Whisper twice — once for Japanese transcription, once for English translation. Results appear in a rolling terminal display.

## Requirements

- macOS (tested on Apple Silicon)
- Python 3.10+
- [BlackHole](https://github.com/ExistentialAudio/BlackHole) (virtual audio driver)
- [FFmpeg](https://ffmpeg.org/)
- [PortAudio](http://www.portaudio.com/)

## Setup

### 1. Install system dependencies

```bash
brew install portaudio blackhole-2ch ffmpeg
```

### 2. Configure audio routing

Set up a Multi-Output Device in macOS so you can hear Meet audio and capture it simultaneously. See [setup_audio.md](setup_audio.md) for step-by-step instructions.

### 3. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Verify BlackHole is detected
python main.py --list-devices

# Start live translation (downloads model on first run)
python main.py
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `medium` | Whisper model: `tiny`, `base`, `small`, `medium`, `large`, `large-v3` |
| `--device` | `mps` | Compute device: `mps` (Apple Silicon), `cpu`, `cuda` |
| `--chunk-duration` | `5.0` | Seconds per audio chunk |
| `--audio-device` | `BlackHole 2ch` | Input device name |
| `--list-devices` | | List audio devices and exit |

### Examples

```bash
# Faster, less accurate
python main.py --model small

# Best accuracy (needs ~10GB memory)
python main.py --model large-v3

# Lower latency with shorter chunks
python main.py --chunk-duration 3
```

## Expected latency

~10 seconds from speech to translation (5s chunk + ~5s processing on Apple Silicon with `medium` model).

## License

MIT
