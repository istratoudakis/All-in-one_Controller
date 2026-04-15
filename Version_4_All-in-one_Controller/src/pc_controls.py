import pyautogui
import comtypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, GUID
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IMMDeviceEnumerator
import os
import subprocess

try:
    import psutil
except ImportError:
    print("Cpu fail")
try:
    import GPUtil
except ImportError:
    GPUtil = None

# ==========================================
# --- GLOBAL AUDIO INITIALIZATION ---
# ==========================================
try:
    comtypes.CoInitialize()
    
    # Ζητάμε απευθείας από τα Windows το κεντρικό ηχείο (eRender)
    CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
    deviceEnumerator = comtypes.CoCreateInstance(
        CLSID_MMDeviceEnumerator,
        IMMDeviceEnumerator,
        CLSCTX_ALL
    )
    
    # 0 = eRender (Ηχεία), 1 = eMultimedia
    endpoint = deviceEnumerator.GetDefaultAudioEndpoint(0, 1)
    
    # Ενεργοποιούμε το Volume Interface για τα Ηχεία
    interface = endpoint.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control = cast(interface, POINTER(IAudioEndpointVolume))
    
    print("✅ Το Σύστημα Ήχου (Raw API) αρχικοποιήθηκε επιτυχώς!")
except Exception as e:
    print(f"❌ Σφάλμα κατά την αρχικοποίηση του ήχου: {e}")
    volume_control = None

# --- Paths για το NirCmd (χρησιμοποιείται για το Mic Mute Toggle) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
possible_nircmd_paths = [
    os.path.join(current_dir, "nircmd.exe"),
    os.path.join(current_dir, "..", "nircmd.exe")
]

# ==========================================
# --- FUNCTIONS ---
# ==========================================

def get_hardware_stats():
    """Επιστρέφει τη χρήση CPU, RAM και GPU σε ακέραια ποσοστά (0-100)"""
    # Το interval=None εξασφαλίζει ότι η εντολή δεν θα μπλοκάρει (δεν θα παγώσει) τον κώδικα
    cpu = int(psutil.cpu_percent(interval=None))
    ram = int(psutil.virtual_memory().percent)
    
    gpu = 0
    # Διαβάζουμε την κάρτα γραφικών (με ασφάλεια σε περίπτωση που δεν βρεθεί)
    if GPUtil is not None:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = int(gpus[0].load * 100)
            
    return cpu, ram, gpu

def get_pc_volume():
    """Διαβάζει την ένταση των Windows (0-100) ΑΣΤΡΑΠΙΑΙΑ"""
    if not volume_control: return 50
    try:
        return int(volume_control.GetMasterVolumeLevelScalar() * 100)
    except Exception as e:
        print(f"[ERROR] Volume Read Failed: {e}") 
        return 50 

def set_volume(level):
    """
    Ρυθμίζει την ένταση των Windows. 
    Υποστηρίζει απόλυτες τιμές (0-100) και σχετικές τιμές ("+10", "-10").
    """
    if not volume_control or level is None: return
    
    try:
        current_vol = get_pc_volume()
        target_vol = current_vol

        # Έλεγχος αν η τιμή είναι σχετική (String με + ή -)
        if isinstance(level, str):
            if level.startswith('+'):
                target_vol = current_vol + int(level[1:])
            elif level.startswith('-'):
                target_vol = current_vol - int(level[1:])
            else:
                target_vol = int(level)
        else:
            target_vol = int(level)

        # Περιορισμός τιμών ασφαλείας μεταξύ 0 και 100
        final_level = max(0, min(100, target_vol))
        
        # Το API δέχεται τιμές από 0.0 έως 1.0
        volume_control.SetMasterVolumeLevelScalar(final_level / 100, None)
        print(f"[PC CONTROL] Volume adjusted from {current_vol}% to {final_level}%")
        
    except Exception as e:
        print(f"❌ Error setting volume: {e}")

def set_mic_volume(level):
    """Ρυθμίζει την ένταση του Μικροφώνου στα Windows (0-100)"""
    try:
        comtypes.CoInitialize() 
        devices = AudioUtilities.GetMicrophone()
        if not devices: 
            print("⚠️ Δεν βρέθηκε μικρόφωνο!")
            return
        
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        mic_volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        level = max(0, min(100, int(level)))
        mic_volume.SetMasterVolumeLevelScalar(level / 100, None)
        print(f"🎤 [PC CONTROL] Microphone volume set to {level}%")
    except Exception as e:
        print(f"❌ Error setting mic volume: {e}")

def toggle_system_mic_mute():
    """Χρησιμοποιεί το NirCmd για Toggle Mute του μικροφώνου."""
    nircmd_exe = None
    for path in possible_nircmd_paths:
        if os.path.exists(path):
            nircmd_exe = path
            break
    
    if not nircmd_exe:
        print(f"❌ ΣΦΑΛΜΑ: Το nircmd.exe δεν βρέθηκε!")
        return

    try:
        # 2 = toggle
        subprocess.run([nircmd_exe, "mutesysvolume", "2", "default_record"], check=True)
        print("✅ Mic Toggled Successfully via NirCmd")
    except Exception as e:
        print(f"❌ Error toggling mic: {e}")

def boss_key():
    """Win + D shortcut (Ελαχιστοποίηση / Desktop)"""
    try:
        pyautogui.hotkey('win', 'd')
        print("[PC CONTROL] Boss Key activated!")
    except Exception as e:
        print(f"Error with Boss Key: {e}")

def toggle_camera():
    """Ανοίγει την εφαρμογή κάμερας των Windows"""
    try:
        os.system("start microsoft.windows.camera:")
        print("[PC CONTROL] Camera app toggled")
    except Exception as e:
        print(f"Error toggling camera: {e}")

def media_play_pause():
    """Play/Pause για media players"""
    try:
        pyautogui.press('playpause')
        print("[PC CONTROL] Media Play/Pause")
    except Exception as e:
        print(f"Error with Play/Pause: {e}")