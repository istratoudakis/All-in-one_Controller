import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import psutil
import time

def set_volume(level):
    try:
        if level is None: return
        level = max(0, min(100, int(level)))
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        print(f"[PC CONTROL] Volume set to {level}%")
    except Exception as e:
        print(f"Error setting volume: {e}")

def toggle_mute():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_mute = volume.GetMute()
        volume.SetMute(not current_mute, None)
    except Exception as e:
        print(f"Error toggling mute: {e}")

def boss_key():
    pyautogui.hotkey('win', 'd')

def toggle_camera():
    os.system("start microsoft.windows.camera:")

def get_system_stats():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return int(cpu), int(ram)

def open_study_apps():
    # Μπορείς να προσθέσεις εδώ paths για PDF ή φακέλους
    print("[SYSTEM]: Focus Mode Activated - Ready to study.")

def save_smart_note(note_text, category="GENERAL"):
    """Αποθηκεύει τη σημείωση σε φακέλους ανάλογα με την κατηγορία στο Desktop."""
    try:
        # Δημιουργία κεντρικού φακέλου "AI_Notes" στο Desktop
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        base_path = os.path.join(desktop, "AI_Notes")
        
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # Ορισμός αρχείου βάσει κατηγορίας (π.χ. UNIVERSITY.txt)
        file_path = os.path.join(base_path, f"{category.upper()}.txt")
        
        with open(file_path, "a", encoding="utf-8") as f:
            timestamp = time.strftime('%d/%m/%Y %H:%M')
            f.write(f"[{timestamp}] {note_text}\n")
        
        print(f"[PC CONTROL]: Note archived in {category}.txt")
    except Exception as e:
        print(f"[ERROR]: Could not save smart note: {e}")

def enforce_pomodoro():
    browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"]
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() in browsers:
                print(f"[POMODORO]: Distraction detected -> {proc.info['name']}")
    except:
        pass