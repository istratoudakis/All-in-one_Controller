import sys
import os
import json

# Προσθήκη του φακέλου src για να βρίσκει τα modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_handler import parse_voice_command
from serial_bridge import execute_ai_commands

def run_text_test():
    print("\n" + "="*40)
    print("      GEMINI TEXT-TO-ACTION TEST")
    print("="*40)
    
    # 1. Παίρνουμε την εντολή γραπτά
    user_input = input("\nΓράψε μια εντολή (π.χ. 'Volume 50' ή 'Next song'): ")
    
    if not user_input.strip():
        print("Δεν έγραψες τίποτα!")
        return

    # 2. Στέλνουμε στο Gemini
    print("\n[1/2] Sending to Gemini...")
    result = parse_voice_command(user_input)
    
    if result:
        print("\n=== GEMINI ANALYSIS ===")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        # 3. Εκτέλεση στο PC
        print("\n[2/2] Executing commands on PC...")
        # Περνάμε None αντί για Serial αφού δεν έχουμε ESP32
        execute_ai_commands(result, None)
        
        print("\n" + "="*40)
        print("   DONE! Check your Volume/Spotify")
        print("="*40)
    else:
        print("\n[!] Gemini failed to respond. Check your API Key.")

if __name__ == "__main__":
    run_text_test()