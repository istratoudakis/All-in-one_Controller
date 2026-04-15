#include <Arduino.h>

// Ορισμός Pins για τα 3 Κουμπιά
const int btnScreenShare = 18; 
const int btnBRB         = 19;
const int btnOnAir       = 21;

// Ορισμός Pins για τα 2 LEDs
const int ledOnAir       = 5;  // Ανάβει όταν είμαστε Live
const int ledConnection  = 4;  // Δείχνει το status της σύνδεσης

void setup() {
  Serial.begin(115200);

  // Ρύθμιση Κουμπιών ως Είσοδοι με εσωτερική αντίσταση (PULLUP)
  pinMode(btnScreenShare, INPUT_PULLUP);
  pinMode(btnBRB,         INPUT_PULLUP);
  pinMode(btnOnAir,       INPUT_PULLUP);

  // Ρύθμιση LEDs ως Έξοδοι
  pinMode(ledOnAir,      OUTPUT);
  pinMode(ledConnection, OUTPUT);

  // Αρχικό status: Το connection LED αναβοσβήνει 3 φορές στην εκκίνηση
  for(int i=0; i<3; i++) {
    digitalWrite(ledConnection, HIGH); delay(200);
    digitalWrite(ledConnection, LOW);  delay(200);
  }
}

void loop() {
  // 1. Έλεγχος Κουμπιού Screen Share
  if (digitalRead(btnScreenShare) == LOW) {
    Serial.println("<CMD:SCREEN_SHARE>"); 
    delay(300); // Debouncing
  }

  // 2. Έλεγχος Κουμπιού BRB
  if (digitalRead(btnBRB) == LOW) {
    Serial.println("<CMD:BRB>"); // ΝΕΑ ΜΟΡΦΗ
    delay(300);
  }

  // 3. Έλεγχος Κουμπιού On Air (Start/Stop Stream)
  if (digitalRead(btnOnAir) == LOW) {
    Serial.println("<CMD:ON_AIR_TOGGLE>"); // ΝΕΑ ΜΟΡΦΗ
    delay(300);
  }

  // 4. "Ακρόαση" από το PC για τα LEDs (Αμφίδρομη Επικοινωνία)
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    message.trim();

    // ΝΕΑ ΜΟΡΦΗ ΓΙΑ ΤΗ ΛΗΨΗ ΕΝΤΟΛΩΝ
    if (message == "<LED:ONAIR_ON>")   digitalWrite(ledOnAir, HIGH);
    if (message == "<LED:ONAIR_OFF>")  digitalWrite(ledOnAir, LOW);
    if (message == "<LED:CONN_ON>")    digitalWrite(ledConnection, HIGH);
    if (message == "<LED:CONN_OFF>")   digitalWrite(ledConnection, LOW);
  }
}