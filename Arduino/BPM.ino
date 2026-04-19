#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#define USE_ARDUINO_INTERRUPTS true
#include <PulseSensorPlayground.h>

const int PULSE_PIN = A0;
const int LED_PIN = 13;
const int BUZZER_PIN = 11;

const int THRESHOLD = 550;
const int MIN_BPM = 50;
const int MAX_BPM = 140;

PulseSensorPlayground sensor;
LiquidCrystal_I2C lcd(0x27, 16, 2);

int bpm = 0;
int smoothBPM = 0;
unsigned long lastSignal = 0;

String getStatus(int value) {
  if (value < 60) return "Low";
  if (value <= 100) return "Normal";
  if (value <= 120) return "Elevated";
  return "High";
}

void beep() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(25);
  digitalWrite(BUZZER_PIN, LOW);
}

void setup() {
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  sensor.analogInput(PULSE_PIN);
  sensor.blinkOnPulse(LED_PIN);
  sensor.setThreshold(THRESHOLD);
  sensor.begin();

  lcd.setCursor(0, 0);
  lcd.print("Heart Monitor");
  delay(1200);
  lcd.clear();
}

void loop() {
  bpm = sensor.getBeatsPerMinute();

  if (bpm >= MIN_BPM && bpm <= MAX_BPM) {
    smoothBPM = (smoothBPM == 0) ? bpm : (smoothBPM * 0.8 + bpm * 0.2);
    lastSignal = millis();

    Serial.print("BPM:");
    Serial.println(smoothBPM);
  }

  if (sensor.sawStartOfBeat() && bpm >= MIN_BPM && bpm <= MAX_BPM) {
    beep();
  }

  lcd.setCursor(0, 0);

  if (millis() - lastSignal > 3000) {
    lcd.print("Place Finger   ");
    lcd.setCursor(0, 1);
    lcd.print("No Signal      ");
    smoothBPM = 0;
  } else {
    String status = getStatus(smoothBPM);

    lcd.print("Status: ");
    lcd.print(status);
    int used = 8 + status.length();
    for (int i = used; i < 16; i++) lcd.print(" ");

    lcd.setCursor(0, 1);
    lcd.print("BPM: ");
    lcd.print(smoothBPM);
    lcd.print("   ");
  }

  delay(200);
}