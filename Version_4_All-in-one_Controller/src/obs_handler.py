import os
import subprocess
import keyboard

def open_obs():
    """
    Αναλαμβάνει να βρει και να ανοίξει το OBS Studio.
    """
    print("🎥 [OBS Handler] Προσπάθεια εκκίνησης του OBS Studio...")
    
    # Διαδρομές εγκατάστασης στα Windows
    obs_paths = [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe"
    ]
    
    for path in obs_paths:
        if os.path.exists(path):
            try:
                working_dir = os.path.dirname(path)
                # Εκκίνηση OBS με το σωστό working directory
                subprocess.Popen([path], cwd=working_dir)
                print("✅ [OBS Handler] Το OBS Studio άνοιξε επιτυχώς!")
                return True
            except Exception as e:
                print(f"❌ [OBS Handler] Σφάλμα κατά το άνοιγμα: {e}")
                return False
                
    print("⚠️ [OBS Handler] Το OBS δεν βρέθηκε στις κλασικές διαδρομές!")
    return False

def set_screen_scene():
    """Εναλλαγή στη σκηνή 'Screen' (Οθόνη)"""
    print("🎥 [OBS] Εναλλαγή σε σκηνή: Screen")
    keyboard.send('ctrl+alt+8')

def set_brb_scene():
    """Εναλλαγή στη σκηνή 'BRB' (Διάλειμμα)"""
    print("🎥 [OBS] Εναλλαγή σε σκηνή: BRB")
    keyboard.send('ctrl+alt+9')

def toggle_recording():
    """Έναρξη ή Διακοπή της καταγραφής βίντεο"""
    print("🎥 [OBS] Έναρξη/Διακοπή Καταγραφής")
    keyboard.send('ctrl+alt+7')