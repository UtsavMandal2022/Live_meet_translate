# Audio Setup Guide (macOS)

This tool captures system audio from Google Meet using BlackHole, a virtual audio loopback driver.

## Step 1: Install BlackHole

```bash
brew install blackhole-2ch
```

## Step 2: Create a Multi-Output Device

This lets you hear the audio AND capture it simultaneously.

1. Open **Audio MIDI Setup** (Spotlight: "Audio MIDI Setup")
2. Click the **+** button at the bottom-left, select **Create Multi-Output Device**
3. Check these boxes in order:
   - Your speakers/headphones (e.g., "MacBook Pro Speakers" or "AirPods")
   - **BlackHole 2ch**
4. Right-click the new Multi-Output Device and select **Use This Device For Sound Output**

## Step 3: Set Google Meet to use the Multi-Output Device

- In **System Settings > Sound > Output**, select the **Multi-Output Device**
- Alternatively, Option-click the volume icon in the menu bar to switch output

## Step 4: Verify

Run:
```bash
python main.py --list-devices
```

You should see "BlackHole 2ch" in the device list. If not, restart your Mac after installing BlackHole.

## Troubleshooting

- **No audio captured**: Make sure the Multi-Output Device is set as system output
- **BlackHole not showing up**: Restart after `brew install blackhole-2ch`
- **Echo/feedback**: Make sure your microphone input is NOT set to BlackHole
- **Low volume**: In Audio MIDI Setup, ensure both devices in the Multi-Output have the same sample rate (44100 or 48000 Hz)
