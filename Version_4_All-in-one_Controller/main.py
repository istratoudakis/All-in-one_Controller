import os
import subprocess

# 1. Καθορίζουμε τις πιθανές διαδρομές έξω από τη συνάρτηση (για να υπολογίζονται μία φορά)
current_dir = os.path.dirname(os.path.abspath(__file__))

possible_nircmd_paths = [
    os.path.join(current_dir, "nircmd.exe"),          # Αν είναι μέσα στο src/
    os.path.join(current_dir, "..", "nircmd.exe")    # Αν είναι στη ρίζα (root)
]

def toggle_system_mic_mute():
    """
    Εναλλάσσει το Mute του μικροφώνου χρησιμοποιώντας την απόλυτη διαδρομή του NirCmd.
    """
    nircmd_exe = None
    
    # Αναζήτηση του αρχείου στις πιθανές τοποθεσίες
    for path in possible_nircmd_paths:
        if os.path.exists(path):
            nircmd_exe = path
            break
    
    if not nircmd_exe:
        print(f"❌ ΣΦΑΛΜΑ: Το nircmd.exe δεν βρέθηκε! Έγινε έλεγχος στα: {possible_nircmd_paths}")
        return

    try:
        # Εκτέλεση με την απόλυτη διαδρομή για να μην μπερδεύεται το .venv
        subprocess.run([nircmd_exe, "mutesysvolume", "2", "default_record"], check=True)
        
        # Προαιρετικό: Πέτα και μια ειδοποίηση στα Windows για να το βλέπεις
        subprocess.run([nircmd_exe, "trayballoon", "Mute Control", "Το μικρόφωνο άλλαξε!", "1", "1000"])
        
        print(f"✅ Mic Toggled Successfully (using: {nircmd_exe})")
    except Exception as e:
        print(f"❌ Error during NirCmd execution: {e}")

# Τεστ λειτουργίας
if __name__ == "__main__":
    toggle_system_mic_mute()