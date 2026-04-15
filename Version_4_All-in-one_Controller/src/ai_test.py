import time
import os
# Εισαγωγή των δικών σου κλάσεων/συναρτήσεων
from ai_handler import parse_voice_command
from voice_recorder import VoiceRecorder
# Χρειαζόμαστε και τον processor για να μετατρέψει το WAV σε κείμενο
from voice_processor import convert_voice_to_text 
# Εισαγωγή των πραγματικών ελέγχων του PC
from pc_controls import set_volume, boss_key, toggle_camera, toggle_system_mic_mute
from spotify_handler import spotify_control

def execute_pc_action(commands):
    """Εκτελεί τις εντολές που επέστρεψε το AI απευθείας στο PC"""
    if not commands: return

    print(f"\n⚙️ [EXECUTING]: {commands}")

    # 1. Volume
    if commands.get('volume') is not None:
        print(f"🔊 Setting Volume to: {commands['volume']}")
        set_volume(commands['volume'])

    # 2. Spotify
    if commands.get('spotify') != "NONE":
        print(f"🎵 Spotify Action: {commands['spotify']}")
        spotify_control(commands['spotify'])

    # 3. Boss Key
    if commands.get('boss_key'):
        print("🤫 Boss Key Activated!")
        boss_key()

    # 4. Mic Mute
    if commands.get('mic_mute'):
        print("🎙️ System Mic Mute Toggled!")
        toggle_system_mic_mute()

    # 5. Camera
    if commands.get('camera') == "TOGGLE":
        print("📷 Camera Toggled!")
        toggle_camera()

def run_simulator():
    recorder = VoiceRecorder()
    print("\n=== 🎙️ AI VOICE COMMAND SIMULATOR (NO ESP32) ===")
    print("Οδηγίες: Πάτα ENTER για να ξεκινήσει η εγγραφή και ENTER ξανά για να σταματήσει.")

    try:
        while True:
            input("\n>>> Πάτα [ENTER] για να μιλήσεις...")
            
            # Ξεκινάει η εγγραφή
            recorder.start_recording()
            print("🔴 Recording... (Πάτα ENTER για STOP)")
            
            # Loop όσο γράφει (προσομοιώνει το record_chunk)
            # Στο simulator απλά περιμένουμε το επόμενο ENTER
            import threading
            stop_event = threading.Event()

            def wait_for_stop():
                input()
                stop_event.set()

            t = threading.Thread(target=wait_for_stop)
            t.start()

            while not stop_event.is_set():
                recorder.record_chunk()
                time.sleep(0.01)

            # Σταματάει η εγγραφή
            file_path = recorder.stop_recording()
            print("💾 Audio saved. Processing...")

            # Μετατροπή σε κείμενο (χρησιμοποιεί το DSP που φτιάξαμε)
            text = convert_voice_to_text(file_path)
            
            if text:
                print(f"📝 Recognized: {text}")
                # Ανάλυση με AI ή Local Parser
                commands = parse_voice_command(text)
                # Εκτέλεση
                execute_pc_action(commands)
                print(f"✨ Feedback for ESP32: {commands.get('feedback')}")
            else:
                print("❌ Δεν αναγνωρίστηκε φωνή.")

    except KeyboardInterrupt:
        print("\n👋 Simulator closed.")

if __name__ == "__main__":
    run_simulator()