"""
Audio FFT -> Serial (Bass / Mid / High)

- Captures system audio via WASAPI loopback
- Computes FFT and band energy
- Sends space-separated values to microcontroller

Serial format:
    <bass> <mid> <high>\n
"""

import pyaudiowpatch as pyaudio
import numpy as np
import serial
import time

# --------------------
# Audio configuration
# --------------------
RATE = 44100          # Sample rate (match system)
CHUNK = 1024          # FFT size
CHANNELS = 2

# --------------------
# Serial configuration
# --------------------
SERIAL_PORT = "COM9"  # Change as needed
BAUD_RATE = 115200

# --------------------
# FFT bands (Hz)
# --------------------
BASS_RANGE = (20, 250)
MID_RANGE  = (250, 4000)
HIGH_RANGE = (4000, 20000)

# Scaling factor (adjust for sensitivity)
GAIN = 10

# --------------------
# Serial init
# --------------------
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # allow MCU reset

# --------------------
# PyAudio init
# --------------------
p = pyaudio.PyAudio()

print("Available loopback devices:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if '[Loopback]' in info.get('name', ''):
        print(i, info['name'])

loopback_index = int(input("Select loopback device index: "))

stream = p.open(
    format=pyaudio.paFloat32,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=loopback_index,
    frames_per_buffer=CHUNK
)

# --------------------
# FFT preparation
# --------------------
freqs = np.fft.rfftfreq(CHUNK, d=1.0 / RATE)

bass_band = (freqs >= BASS_RANGE[0]) & (freqs < BASS_RANGE[1])
mid_band  = (freqs >= MID_RANGE[0])  & (freqs < MID_RANGE[1])
high_band = (freqs >= HIGH_RANGE[0]) & (freqs < HIGH_RANGE[1])

print("Capturing audio... Press Ctrl+C to stop")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.float32)

        # Stereo → mono
        samples = samples.reshape(-1, CHANNELS).mean(axis=1)

        # FFT
        fft = np.fft.rfft(samples)
        mag = np.abs(fft)

        # RMS energy per band
        bass = np.sqrt(np.mean(mag[bass_band] ** 2))
        mid  = np.sqrt(np.mean(mag[mid_band] ** 2))
        high = np.sqrt(np.mean(mag[high_band] ** 2))

        # Scale + clamp
        bass = min(int(bass * GAIN), 255)
        mid  = min(int(mid  * GAIN), 255)
        high = min(int(high * GAIN), 255)

        # Send to MCU
        ser.write(f"{bass} {mid} {high}\n".encode())

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    ser.close()
