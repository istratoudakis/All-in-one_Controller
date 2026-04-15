from voice_recorder import VoiceRecorder
from voice_processor import convert_voice_to_text
import time

recorder = VoiceRecorder()

print("Μίλα τώρα για 3 δευτερόλεπτα...")
recorder.start_recording()
start = time.time()
while time.time() - start < 3:
    recorder.record_chunk()

path = recorder.stop_recording()
text = convert_voice_to_text(path)

if text:
    print(f"ΕΠΙΤΥΧΙΑ! Το κείμενο είναι: {text}")
else:
    print("Κάτι πήγε στραβά με τη μετατροπή.")