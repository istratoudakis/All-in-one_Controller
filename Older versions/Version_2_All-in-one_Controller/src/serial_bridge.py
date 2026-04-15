import serial
import re
import time
import keyboard
import sys
import ctypes

# --- ΟΙ ΝΕΟΙ HANDLERS ΣΟΥ ΕΝΕΡΓΟΙ ---
from zoom_handler import handle_zoom
from discord_handler_keys import handle_discord_shortcuts
from custom_keys_handler import CustomLinks
from gui_handler import launch_apps_gui

# --- Εισαγωγή των κεντρικών λειτουργιών της ομάδας ΕΝΕΡΓΟΙ ---
from pc_controls import boss_key, toggle_camera, set_volume, get_pc_volume
from spotify_handler import get_spotify_detailed_data, spotify_control
from discord_handler import start_discord_rpc, get_discord_state
from voice_recorder import VoiceRecorder
from voice_processor import convert_voice_to_text
from ai_handler import parse_voice_command

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM3" 
BAUD_RATE = 115200

# --- ΕΝΕΡΓΟ: AI Commands Logic ---
def execute_ai_commands(commands, ser):
    if not commands or "error" in commands: return
    
    # Spotify Control
    if commands.get('spotify') != "NONE":
        spotify_control(commands['spotify'])

    # Volume Control
    if commands.get('volume') is not None:
        set_volume(commands['volume'])
        if ser: ser.write(f"<VOL:{commands['volume']}>\n".encode('utf-8'))
    
    # Boss Key
    if commands.get('boss_key'):
        boss_key()
    
    # Camera
    if commands.get('camera') == "TOGGLE":
        toggle_camera()

    # App Control (Discord/Zoom/OBS)
    app_cmds = commands.get('app_control', [])
    if isinstance(app_cmds, list):
        for cmd in app_cmds:
            if "ZOOM" in cmd: handle_zoom(cmd)
            elif "DISCORD" in cmd: handle_discord_shortcuts(cmd)
    
    # Feedback στην οθόνη του ESP32
    if ser and commands.get('feedback'):
        ser.write(f"{commands['feedback']}\n".encode('utf-8'))

def start_bridge(port_name=PORT):
    recorder = VoiceRecorder()
    ser = None
    
    last_vol = -1
    last_discord_mic = ""
    last_discord_deaf = ""

    # 1. ΕΚΚΙΝΗΣΗ ΤΟΥ GUI & ΣΥΝΔΕΣΗ ΜΕ ΤΑ CUSTOM LINKS
    user_data = launch_apps_gui()
    my_links = user_data.get("links", ["", "", ""])
    links_handler = CustomLinks(my_links)

    # 2. ΑΘΟΡΥΒΗ ΛΕΙΤΟΥΡΓΙΑ Ή DEV CONSOLE 
    if user_data.get("dev_mode"):
        try:
            ctypes.windll.kernel32.FreeConsole()
            ctypes.windll.kernel32.AllocConsole()
            sys.stdout = open("CONOUT$", "w", encoding="utf-8")
            sys.stderr = open("CONOUT$", "w", encoding="utf-8")
            print("=== ESP32 Dashboard: Developer Console Active ===")
        except: pass
    else:
        try:
            hWnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hWnd != 0: ctypes.windll.user32.ShowWindow(hWnd, 0)
        except: pass
    
    # ΕΝΕΡΓΟ: Discord RPC/Status Tracking
    start_discord_rpc()

    try:
        ser = serial.Serial(port_name, BAUD_RATE, timeout=0.1)
        print(f"--- 🚀 Bridge Active on {port_name} ---")
        
        print("Περιμένω 5 δευτερόλεπτα να ανοίξει η οθόνη του ESP32...")
        time.sleep(5) 
        ser.write(b"<PC_OK>\n")
        time.sleep(1)
        
        last_sync_time = 0 
        print("Ξεκινάει το Main Loop! (Ctrl+C για έξοδο)")

        while True:
            # ΕΝΕΡΓΟ: Recording Chunk
            if recorder.is_recording: 
                recorder.record_chunk()

            current_time = time.time()
            
            # --- 🔄 SYNC LOOP (Spotify, Volume, Discord) ---
            if current_time - last_sync_time >= 1.0:
                last_sync_time = current_time
                
                # Spotify Data
                spot_data = get_spotify_detailed_data()
                if spot_data and ser:
                    for key, value in spot_data.items():
                        ser.write(f"{value}\n".encode('utf-8'))
                        time.sleep(0.01) 
                
                # Volume Sync
                current_vol = get_pc_volume()
                if current_vol != last_vol:
                    last_vol = current_vol
                    if ser: ser.write(f"<VOL:{current_vol}>\n".encode('utf-8'))
                
                # Discord Sync
                d_state = get_discord_state()
                if d_state["mic"] != last_discord_mic:
                    last_discord_mic = d_state["mic"]
                    cmd = "<MIC:OFF>\n" if last_discord_mic == "MUTED" else "<MIC:ON>\n"
                    if ser: ser.write(cmd.encode('utf-8'))

                if d_state["deaf"] != last_discord_deaf:
                    last_discord_deaf = d_state["deaf"]
                    cmd = "<DISC:DEAF>\n" if last_discord_deaf == "ON" else "<DISC:UNDEAF>\n"
                    if ser: ser.write(cmd.encode('utf-8'))

            # --- 📥 ΑΝΑΓΝΩΣΗ ΕΝΤΟΛΩΝ ΑΠΟ ΤΟ ESP32 ---
            if ser and ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line: print(f"ESP32 Signal: {line}")
                
                # Άμεσες εντολές String (Links, Zoom, Discord)
                if line in ["LINK_1", "LINK_2", "LINK_3"]:
                    links_handler.open(line)
                    continue
                elif line in ["ZOOM_MUTE", "ZOOM_CAMERA", "ZOOM_HAND", "ZOOM_LEAVE"]:
                    handle_zoom(line)
                    continue
                elif line in ["DISCORD_MUTE", "DISCORD_DEAFEN"]:
                    handle_discord_shortcuts(line)
                    continue

                match = re.match(r"<(.*):(.*)>", line)
                if match:
                    key, value = match.group(1), match.group(2)

                    if key == "BTN":
                        if value == "SPOT_TOGGLE": spotify_control("TOGGLE")
                        elif value == "NEXT": spotify_control("NEXT")
                        elif value == "PREV": spotify_control("PREV")
                        elif value == "BOSS_KEY": boss_key()
                        elif value == "CAMERA": toggle_camera()
                        
                        # Fallback για τα string commands μέσα σε BTN tag
                        elif value in ["LINK_1", "LINK_2", "LINK_3"]: links_handler.open(value)
                        elif value in ["ZOOM_MUTE", "ZOOM_CAMERA", "ZOOM_HAND", "ZOOM_LEAVE"]: handle_zoom(value)
                        elif value in ["DISCORD_MUTE", "DISCORD_DEAFEN"]: handle_discord_shortcuts(value)
                        
                        print(f"▶️ [HW BTN] {value} Executed")
                        continue

                    if key == "VOICE":
                        if value == "START":
                            recorder.start_recording()
                            ser.write(b"<AI:LISTENING>\n")
                        
                        elif value == "STOP":
                            ser.write(b"<AI:THINKING>\n")
                            path = recorder.stop_recording()
                            text = convert_voice_to_text(path)
                            
                            if text == "ERROR_OFFLINE":
                                ser.write(b"<AI:OFFLINE>\n")
                                continue

                            if text:
                                commands = parse_voice_command(text)
                                execute_ai_commands(commands, ser)
                            else:
                                ser.write(b"<AI:RETRY>\n")
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n👋 Κλείσιμο Bridge...")
    except Exception as e:
        print(f"\n❌ Κρίσιμο Σφάλμα: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()

if __name__ == "__main__":
    start_bridge()