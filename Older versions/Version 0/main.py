import time
import sys
import os
import json # Προστέθηκε για το formatting του JSON

# Προσθήκη του src στο path για να βρίσκει τα modules σωστά
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.serial_bridge import execute_ai_commands
from src.voice_recorder import VoiceRecorder
from src.voice_processor import convert_voice_to_text
from src.ai_handler import parse_voice_command

def run_simulation():
    recorder = VoiceRecorder()
    print("\n" + "="*45)
    print("   ALL-IN-ONE CONTROLLER (SIMULATION)")
    print("="*45)
    print("Commands:")
    print(" - Press ENTER to start recording (Simulates ESP32 button)")
    print(" - Type 'q' and ENTER to exit")

    while True:
        user_input = input("\n[READY] > ").strip().lower()
        
        if user_input == 'q':
            print("[INFO]: Εξοδος από το πρόγραμμα...")
            break
            
        # Προσομοίωση <VOICE:START>
        print("\n[SIM]: <MIC:LISTENING> (Μίλα τώρα...)")
        recorder.start_recording()
        
        # Ηχογράφηση για 5 δευτερόλεπτα με οπτικό feedback
        start_time = time.time()
        while time.time() - start_time < 5:
            recorder.record_chunk()
            print(".", end="", flush=True)
            time.sleep(0.1)
            
        # Προσομοίωση <VOICE:STOP>
        path = recorder.stop_recording()
        print("\n[SIM]: <AI:THINKING> (Ανάλυση από Gemini...)")
        
        # 1. Επεξεργασία Φωνής (Speech to Text)
        text = convert_voice_to_text(path)
        
        if text:
            print(f"\n[VOICE]: {text}")
            
            # 2. Ανάλυση Gemini (Text to JSON)
            commands = parse_voice_command(text)
            
            if commands:
                # --- ΕΔΩ ΤΥΠΩΝΟΥΜΕ ΤΟ JSON ΠΟΥ ΖΗΤΗΣΕΣ ---
                print("\n" + "-"*20)
                print("[DEBUG JSON FROM GEMINI]:")
                print(json.dumps(commands, indent=4, ensure_ascii=False))
                print("-"*20)
                
                # 3. Εκτέλεση (Το ser=None σημαίνει simulation - τυπώνει μόνο το Πρωτόκολλο)
                print("\n[EXECUTING ACTIONS]:")
                execute_ai_commands(commands, None)
                
            else:
                print("[ERROR]: Το Gemini δεν επέστρεψε έγκυρο JSON.")
        else:
            print("\n[SIM]: <AI:RETRY> (Δεν ανιχνεύθηκε ομιλία)")

if __name__ == "__main__":
    run_simulation()