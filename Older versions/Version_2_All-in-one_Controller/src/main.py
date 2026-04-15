import time
from pc_controls import execute_actions, toggle_mute, get_pc_volume

def run_mute_test():
    print("--- 🔇 Ξεκινάει το Mute/Unmute Test ---")

    # 1. Έλεγχος Τρέχουσας Κατάστασης
    current_vol = get_pc_volume()
    print(f"📊 Αρχική Ένταση: {current_vol}%")

    # 2. Test: System Mute (Windows Master Mute)
    print("\n[STEP 1]: Εναλλαγή System Mute (Windows Master)...")
    toggle_mute() # Καλεί απευθείας τη συνάρτηση από το pc_controls
    print("📢 Το σήμα εστάλη στα Windows.")
    time.sleep(2)
    
    print("[STEP 2]: Επαναφορά System Sound (Unmute)...")
    toggle_mute()
    time.sleep(1)

    # 3. Test: Discord Mute (Focus + Shortcut)
    print("\n[STEP 3]: Δοκιμή Discord Mic Mute (CTRL+SHIFT+M)...")
    print("Σημείωση: Πρέπει να έχεις το Discord ανοιχτό για να δεις το Focus.")
    
    # Χρησιμοποιούμε την execute_actions για να προσομοιώσουμε σήμα από ESP32/AI
    mute_command = {
        "mic_mute": True, 
        "feedback": "TESTING DISCORD MUTE"
    }
    execute_actions(mute_command)
    
    time.sleep(3) # Σου δίνει χρόνο να δεις αν άλλαξε το εικονίδιο στο Discord

    # 4. Test: Discord Deafen (Focus + Shortcut)
    print("\n[STEP 4]: Δοκιμή Discord Deafen (CTRL+SHIFT+D)...")
    
    deafen_command = {
        "app_control": ["DISCORD_DEAFEN"], 
        "feedback": "TESTING DISCORD DEAFEN"
    }
    execute_actions(deafen_command)
    
    print("\n--- ✅ Το Mute Test Ολοκληρώθηκε ---")

if __name__ == "__main__":
    run_mute_test()