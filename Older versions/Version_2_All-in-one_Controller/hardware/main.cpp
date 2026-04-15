#include <Arduino.h>

// ==========================================
// --- ΡΥΘΜΙΣΕΙΣ PINS (ESP32) ---
// ==========================================

// Pins για το OBS Studio
const int btnScreenShare = 18; 
const int btnBRB         = 19;
const int btnOnAir       = 21;

// Pins για την "Νησίδα Επικοινωνίας"
const int switchMode = 25; // Ο Διακόπτης (Πάνω=Discord, Κάτω=Zoom)
const int btnComm1   = 26; // Κουμπί 1: Ήχος (Mute)
const int btnComm2   = 27; // Κουμπί 2: Κάμερα (Video)
const int btnComm3   = 14; // Κουμπί 3: Action (Deafen / Raise Hand)
const int btnComm4   = 12; // Κουμπί 4: Έξοδος (Disconnect / Leave)

// Pins για LEDs
const int ledOnAir       = 5;  
const int ledConnection  = 4;  

void setup() {
  Serial.begin(115200);

  // Ρύθμιση Κουμπιών & Διακόπτη (Χρήση εσωτερικής αντίστασης)
  pinMode(btnScreenShare, INPUT_PULLUP);
  pinMode(btnBRB,         INPUT_PULLUP);
  pinMode(btnOnAir,       INPUT_PULLUP);
  
  pinMode(switchMode, INPUT_PULLUP);
  pinMode(btnComm1,   INPUT_PULLUP);
  pinMode(btnComm2,   INPUT_PULLUP);
  pinMode(btnComm3,   INPUT_PULLUP);
  pinMode(btnComm4,   INPUT_PULLUP);

  // Ρύθμιση LEDs
  pinMode(ledOnAir,      OUTPUT);
  pinMode(ledConnection, OUTPUT);

  // Εφέ Εκκίνησης (Αναβοσβήνει το LED σύνδεσης 3 φορές)
  for(int i=0; i<3; i++) {
    digitalWrite(ledConnection, HIGH); delay(200);
    digitalWrite(ledConnection, LOW);  delay(200);
  }
}

void loop() {
  // ==========================================
  // 1. ΕΛΕΓΧΟΣ ΚΟΥΜΠΙΩΝ OBS (Σταθερά)
  // ==========================================
  if (digitalRead(btnScreenShare) == LOW) {
    Serial.println("<CMD:SCREEN_SHARE>");
    delay(300); 
  }
  if (digitalRead(btnBRB) == LOW) {
    Serial.println("<CMD:BRB>");
    delay(300);
  }
  if (digitalRead(btnOnAir) == LOW) {
    Serial.println("<CMD:ON_AIR_TOGGLE>");
    delay(300);
  }

  // ==========================================
  // 2. ΕΛΕΓΧΟΣ ΕΠΙΚΟΙΝΩΝΙΑΣ (Discord vs Zoom)
  // ==========================================
  // Διαβάζουμε τη θέση του διακόπτη. LOW σημαίνει πατημένος (Discord Mode).
  bool isDiscordMode = (digitalRead(switchMode) == LOW); 

  // ΚΟΥΜΠΙ 1: ΗΧΟΣ
  if (digitalRead(btnComm1) == LOW) {
    if (isDiscordMode) Serial.println("<CMD:DISCORD_MUTE>");
    else               Serial.println("<CMD:ZOOM_MUTE>");
    delay(300);
  }

  // ΚΟΥΜΠΙ 2: ΚΑΜΕΡΑ
  if (digitalRead(btnComm2) == LOW) {
    if (isDiscordMode) Serial.println("<CMD:DISCORD_CAMERA>");
    else               Serial.println("<CMD:ZOOM_CAMERA>");
    delay(300);
  }

  // ΚΟΥΜΠΙ 3: ΔΡΑΣΗ (Action)
  if (digitalRead(btnComm3) == LOW) {
    if (isDiscordMode) Serial.println("<CMD:DISCORD_DEAFEN>");
    else               Serial.println("<CMD:ZOOM_HAND>");
    delay(300);
  }

  // ΚΟΥΜΠΙ 4: ΕΞΟΔΟΣ (Exit)
  if (digitalRead(btnComm4) == LOW) {
    if (isDiscordMode) Serial.println("<CMD:DISCORD_DISCONNECT>");
    else               Serial.println("<CMD:ZOOM_LEAVE>");
    delay(300);
  }

  // ==========================================
  // 3. ΑΚΡΟΑΣΗ ΓΙΑ ΕΝΤΟΛΕΣ LED ΑΠΟ PYTHON
  // ==========================================
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    message.trim();

    if (message == "<LED:ONAIR_ON>")   digitalWrite(ledOnAir, HIGH);
    if (message == "<LED:ONAIR_OFF>")  digitalWrite(ledOnAir, LOW);
    if (message == "<LED:CONN_ON>")    digitalWrite(ledConnection, HIGH);
    if (message == "<LED:CONN_OFF>")   digitalWrite(ledConnection, LOW);
  }
}