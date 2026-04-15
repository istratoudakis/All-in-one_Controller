import serial
import re
import time
import json
import keyboard
import psutil
from pc_controls import (
    set_volume, boss_key, get_system_stats, open_study_apps, 
    save_smart_note, enforce_pomodoro
)
from spotify_handler import get_spotify_detailed_data, spotify_control
from voice_recorder import VoiceRecorder
from voice_processor import convert_voice_to_text
from ai_handler import parse_voice_command

# Καθολικές μεταβλητές
pomodoro_active = False
pomodoro_start_time = 0

def execute_ai_commands(commands, ser):
    """Εκτελεί τις εντολές και στέλνει τα κατάλληλα Tags στην TFT οθόνη."""
    global pomodoro_active, pomodoro_start_time
    
    if not commands or "error" in commands:
        if ser: ser.write(b"<AI:ERROR>\n")
        return

    # --- 1. SMART NOTES ---
    if commands.get('note'):
        category = commands.get('category', 'GENERAL')
        save_smart_note(commands['note'], category)
        # Στέλνουμε feedback στην οθόνη (π.kh. SAVED UNIV)
        if ser: ser.write(f"<AI:SAVED {category[:5].upper()}>\n".encode('utf-8'))

    # --- 2. POMODORO ---
    if commands.get('pomodoro') is True:
        pomodoro_active = True
        pomodoro_start_time = time.time()
        if ser: ser.write(b"<AI:POMO START>\n")

    # --- 3. FOCUS MODE ---
    if commands.get('focus_mode') is True:
        open_study_apps()
        set_volume(20)
        if ser: ser.write(b"<AI:FOCUS ON>\n")

    # --- 4. VOLUME ---
    if commands.get('volume') is not None:
        vol = commands['volume']
        set_volume(vol)
        if ser: ser.write(f"<VOL:{vol}>\n".encode('utf-8'))

    # --- 5. BOSS KEY ---
    if commands.get('boss_key') is True:
        boss_key()
        if ser: ser.write(b"<AI:BOSS MODE>\n")

    # --- 6. SPOTIFY CONTROL ---
    if commands.get('spotify') != "NONE":
        spotify_control(commands['spotify'])
        # Ενημέρωση για την ενέργεια (π.χ. NEXT, TOGGLE)
        if ser: ser.write(f"<AI:SPOT {commands['spotify']}>\n".encode('utf-8'))

    # --- 7. APP CONTROL (Shortcuts) ---
    app_cmd = commands.get('app_control', "NONE")
    if app_cmd != "NONE":
        if app_cmd == "DISCORD_MUTE": keyboard.send("ctrl+alt+shift+m")
        elif app_cmd == "ZOOM_MUTE": keyboard.send("alt+a")
        elif app_cmd == "OBS_START": keyboard.send("f9")
        # Στέλνουμε το όνομα της εφαρμογής στην οθόνη
        if ser: ser.write(f"<AI:{app_cmd[:10]}>\n".encode('utf-8'))

    # --- 8. AI FEEDBACK TEXT ---
    if commands.get('feedback'):
        val = commands['feedback'].upper()[:12]
        if ser: ser.write(f"<AI:{val}>\n".encode('utf-8'))

def start_bridge(port_name="COM3"): # <--- ΠΡΟΣΟΧΗ: Βάλε το δικό σου COM port
    global pomodoro_active, pomodoro_start_time
    recorder = VoiceRecorder()
    ser = None
    last_stats_time = 0
    last_spotify_time = 0
    last_pomodoro_check = 0

    try:
        ser = serial.Serial(port_name, 115200, timeout=0.1)
        ser.flush()
        print(f"--- Bridge Active on {port_name} ---")
        # Στέλνουμε το σήμα ξεκλειδώματος στην οθόνη
        time.sleep(2) # Χρόνος για το reboot του ESP32
        ser.write(b"<PC_OK>\n")
    except Exception as e:
        print(f"[WARNING] Serial Error: {e}. Running in SIMULATION MODE.")

    try:
        while True:
            now = time.time()

            # --- 1. ΦΩΝΗΤΙΚΟΣ ΕΛΕΓΧΟΣ (Με το πλήκτρο F1) ---
            if keyboard.is_pressed('f1'):
                if not recorder.is_recording:
                    recorder.start_recording()
                    if ser: ser.write(b"<AI:LISTENING>\n")
                recorder.record_chunk()
            elif recorder.is_recording:
                if ser: ser.write(b"<AI:THINKING>\n")
                audio_path = recorder.stop_recording()
                text = convert_voice_to_text(audio_path)
                if text:
                    print(f"[USER]: {text}")
                    commands = parse_voice_command(text)
                    execute_ai_commands(commands, ser)
                else:
                    if ser: ser.write(b"<AI:RETRY>\n")

            # --- 2. POMODORO ENFORCER ---
            if pomodoro_active and (now - last_pomodoro_check > 10):
                enforce_pomodoro()
                if now - pomodoro_start_time > 1500: # 25 λεπτά
                    pomodoro_active = False
                    if ser: ser.write(b"<AI:POMO DONE>\n")
                last_pomodoro_check = now

            # --- 3. SYSTEM STATS (CPU/RAM) ---
            if not recorder.is_recording and (now - last_stats_time > 5):
                cpu, ram = get_system_stats()
                # Στέλνουμε το format που περιμένει ο Arduino κώδικας: <SYS:C15R40>
                if ser: ser.write(f"<SYS:C{cpu}R{ram}>\n".encode('utf-8'))
                last_stats_time = now

            # --- 4. SPOTIFY SYNC (OLED/TFT Update) ---
            if not recorder.is_recording and (now - last_spotify_time > 2):
                data = get_spotify_detailed_data()
                if data:
                    # Όνομα τραγουδιού
                    track = data['info'].split("-")[0].strip()[:16].upper()
                    if ser: ser.write(f"<SPOT_INFO:{track}>\n".encode('utf-8'))
                    # Ποσοστό μπάρας
                    if ser: ser.write(f"<SPOT_PERC:{data['perc']}>\n".encode('utf-8'))
                    # Χρονική διάρκεια (αν το υποστηρίζει ο κώδικας οθόνης)
                    if ser: ser.write(f"<SPOT_POS:{data['pos_str']}>\n".encode('utf-8'))
                last_spotify_time = now

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping Bridge...")
    finally:
        if ser: ser.close()

if __name__ == "__main__":
    # Αυτό επιτρέπει το τρέξιμο απευθείας: python src/serial_bridge.py
    start_bridge()