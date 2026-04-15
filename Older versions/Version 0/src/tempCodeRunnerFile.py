import time
import json
import os
import sys

# --- ΔΙΟΡΘΩΣΗ PATHS ΓΙΑ ΤΟ PROJECT ---
current_file_path = os.path.abspath(__file__)
src_folder = os.path.dirname(current_file_path)
project_root = os.path.dirname(src_folder)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from voice_recorder import VoiceRecorder
    from voice_processor import convert_voice_to_text
    from ai_handler import parse_voice_command
    from actions import execute_actions  # <--- ΠΡΟΣΘΗΚΗ
except ImportError as e:
    print(f"\n[ERROR]: Αποτυχία εισαγωγής modules: {e}")
    sys.exit(1)

def run_full_feature_test():
    """
    Εκτελεί ένα πλήρες τεστ: Ηχογράφηση -> Κείμενο -> AI Ανάλυση -> Πραγματικό Action.
    """
    recorder = VoiceRecorder()
    print("\n" + "="*60)
    print("      ALL-IN-ONE CONTROLLER: END-TO-END TEST")
    print("="*60)
    
    # 1. Ηχογράφηση
    print("\nStep 1: Recording for 5 seconds... SPEAK NOW!")
    recorder.start_recording()
    
    start_time = time.time()
    while time.time() - start_time < 5:
        recorder.record_chunk()
        print(".", end="", flush=True)
        time.sleep(0.1)
        
    audio_path = recorder.stop_recording()
    
    # 2. Μετατροπή σε κείμενο
    print("\n\nStep 2: Processing Speech...")
    text = convert_voice_to_text(audio_path)
    
    if not text:
        print("[!] Error: Δεν αναγνωρίστηκε ομιλία.")
        return
        
    print(f"Recognized Text: {text}")

    # 3. Ανάλυση (Local Parser -> AI -> Fallback)
    print("\nStep 3: Analyzing Command...")
    result = parse_voice_command(text)
    
    if result:
        print("\n=== Gemini / Local JSON Response ===")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        # 4. Πραγματική Εκτέλεση στα Windows
        print("\nStep 4: Executing Hardware Actions...")
        try:
            execute_actions(result) # <--- ΕΔΩ ΓΙΝΕΤΑΙ Η ΜΑΓΕΙΑ
            print("\n" + "="*60)
            print("SUCCESS: All actions triggered on your PC!")
            print("="*60)
        except Exception as e:
            print(f"[!] Error during execution: {e}")
            
    else:
        print("\n[!] Error: Parsing failed. Check Quota or Logic.")

if __name__ == "__main__":
    try:
        run_full_feature_test()
    except KeyboardInterrupt:
        print("\nTest interrupted.")