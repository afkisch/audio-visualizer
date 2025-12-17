# Audio Visualizer (Python + NodeMCU)

Real-time audio visualization using:
- Python FFT (system loopback audio)
- Serial communication
- NodeMCU / ESP8266 PWM LED output

## Features
- Bass / Mid / High frequency bands
- Exponential smoothing (EMA)
- Adaptive auto-gain normalization
- Low-latency serial protocol

## Requirements
- Python 3.x
- numpy
- pyserial
- pyaudiowpatch (Windows WASAPI loopback)

## Usage
1. Flash `audio_visualizer.ino` to NodeMCU
2. Connect LEDs to D1 / D2 / D3
3. Run `audio_fft_serial.py`
4. Select loopback device

## Serial Protocol
`<bass> <mid> <high>\n`

Values range 0–255.
