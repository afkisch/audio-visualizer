/*
  Audio Visualizer (ESP8266 / NodeMCU)

  Receives space-separated values over serial:
    bass mid high\n

  Applies:
  - EMA smoothing
  - Adaptive auto-gain (historical max with decay)
  - PWM output to 3 LEDs
*/

int bass = 0;
int mid  = 0;
int high = 0;

// Smoothed values
float bassSmooth = 0;
float midSmooth  = 0;
float highSmooth = 0;

// Adaptive max (auto-gain)
float bassMax = 50;
float midMax  = 50;
float highMax = 50;

// Tuning parameters
const float SMOOTH_ALPHA = 0.25;   // 0.15 smoother | 0.35 snappier
const float MAX_DECAY    = 0.995;  // closer to 1 = slower decay

// GPIO pins (NodeMCU)
const int LED_BASS = D1;
const int LED_MID  = D2;
const int LED_HIGH = D3;

// Safety floor for normalization
const float MIN_MAX = 20.0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5);  // reduce parseInt blocking

  pinMode(LED_BASS, OUTPUT);
  pinMode(LED_MID, OUTPUT);
  pinMode(LED_HIGH, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    // Read space-separated values
    bass = Serial.parseInt();
    mid  = Serial.parseInt();
    high = Serial.parseInt();

    bass = constrain(bass, 0, 255);
    mid  = constrain(mid, 0, 255);
    high = constrain(high, 0, 255);

    // 1) Exponential moving average (EMA)
    bassSmooth += SMOOTH_ALPHA * (bass - bassSmooth);
    midSmooth  += SMOOTH_ALPHA * (mid  - midSmooth);
    highSmooth += SMOOTH_ALPHA * (high - highSmooth);

    // 2) Track historical max with slow decay
    bassMax *= MAX_DECAY;
    if (bassSmooth > bassMax) bassMax = bassSmooth;

    midMax *= MAX_DECAY;
    if (midSmooth > midMax) midMax = midSmooth;

    highMax *= MAX_DECAY;
    if (highSmooth > highMax) highMax = highSmooth;

    // Prevent extreme gain
    if (bassMax < MIN_MAX) bassMax = MIN_MAX;
    if (midMax  < MIN_MAX) midMax  = MIN_MAX;
    if (highMax < MIN_MAX) highMax = MIN_MAX;

    // 3) Normalize to 0–255
    int bassOut = (int)(bassSmooth / bassMax * 255.0);
    int midOut  = (int)(midSmooth  / midMax  * 255.0);
    int highOut = (int)(highSmooth / highMax * 255.0);

    bassOut = constrain(bassOut, 0, 255);
    midOut  = constrain(midOut, 0, 255);
    highOut = constrain(highOut, 0, 255);

    analogWrite(LED_BASS, bassOut);
    analogWrite(LED_MID, midOut);
    analogWrite(LED_HIGH, highOut);
  }
}
