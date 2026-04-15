import pyautogui
import comtypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from comtypes import GUID
from pycaw.pycaw import IAudioEndpointVolume, IMMDeviceEnumerator
import os

# ==========================================
# --- GLOBAL AUDIO INITIALIZATION ---
# ==========================================
try:
    comtypes.CoInitialize()
    
    # Ζητάμε απευθείας από τα Windows το κεντρικό ηχείο (Bypass pycaw wrapper)
    CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
    deviceEnumerator = comtypes.CoCreateInstance(
        CLSID_MMDeviceEnumerator,
        IMMDeviceEnumerator,
        CLSCTX_ALL
    )
    
    # 0 = eRender (Ηχεία), 1 = eMultimedia
    endpoint = deviceEnumerator.GetDefaultAudioEndpoint(0, 1)
    
    # Ενεργοποιούμε το Volume Interface
    interface = endpoint.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control = cast(interface, POINTER(IAudioEndpointVolume))
    
    print("✅ Το Σύστημα Ήχου (Raw API) αρχικοποιήθηκε επιτυχώς!")
except Exception as e:
    print(f"❌ Σφάλμα κατά την αρχικοποίηση του ήχου: {e}")
    volume_control = None

# ==========================================
# --- FUNCTIONS ---
# ==========================================

def get_pc_volume():
    """Διαβάζει την ένταση των Windows (0-100) ΑΣΤΡΑΠΙΑΙΑ και ΑΣΦΑΛΩΣ"""
    if not volume_control: return 50
    try:
        return int(volume_control.GetMasterVolumeLevelScalar() * 100)
    except Exception as e:
        print(f"[ERROR] Volume Read Failed: {e}") 
        return 50 # Σε περίπτωση σφάλματος στέλνει 50 για να μην κρασάρει το ESP32

def set_volume(level):
    """Ρυθμίζει την ένταση των Windows (0-100)"""
    if not volume_control: return
    try:
        if level is None: return
        
        # Περιορισμός τιμών μεταξύ 0 και 100
        level = max(0, min(100, int(level)))
        
        # Το pycaw δέχεται τιμές από 0.0 έως 1.0
        volume_control.SetMasterVolumeLevelScalar(level / 100, None)
        print(f"[PC CONTROL] Volume set to {level}%")
    except Exception as e:
        print(f"Error setting volume: {e}")

def toggle_mute():
    """Κάνει Mute/Unmute τον κεντρικό ήχο"""
    if not volume_control: return
    try:
        current_mute = volume_control.GetMute()
        volume_control.SetMute(not current_mute, None)
        print(f"[PC CONTROL] Mute toggled: {not current_mute}")
    except Exception as e:
        print(f"Error toggling mute: {e}")

def boss_key():
    """Ελαχιστοποιεί τα πάντα (Show Desktop)"""
    try:
        # Win + D shortcut
        pyautogui.hotkey('win', 'd')
        print("[PC CONTROL] Boss Key activated!")
    except Exception as e:
        print(f"Error with Boss Key: {e}")

def toggle_camera():
    """Ανοίγει/Κλείνει την εφαρμογή κάμερας των Windows (Windows 10/11)"""
    try:
        # Στα Windows, το 'start microsoft.windows.camera:' ανοίγει την κάμερα
        os.system("start microsoft.windows.camera:")
        print("[PC CONTROL] Camera app toggled")
    except Exception as e:
        print(f"Error toggling camera: {e}")

def media_play_pause():
    """Play/Pause για οποιοδήποτε media player τρέχει"""
    pyautogui.press('playpause')