import os
import time

def toggle_camera():
    """Ανοίγει την εφαρμογή κάμερας των Windows"""
    try:
        print("📸 Προσπάθεια ανοίγματος της εφαρμογής Κάμερα...")
        # Χρησιμοποιούμε το start για να καλέσουμε το URI των Windows
        os.system("start microsoft.windows.camera:")
        print("✅ [PC CONTROL] Camera app command sent successfully")
    except Exception as e:
        print(f"❌ Error toggling camera: {e}")

def run_camera_test():
    print("--- 📷 Windows Camera Test ---")
    print("Προετοιμασία... (3 δευτερόλεπτα)")
    time.sleep(3)
    
    toggle_camera()
    
    print("\n💡 Σημείωση: Αν η εφαρμογή άνοιξε, ο κώδικας δουλεύει.")
    print("💡 Αν θέλεις να την ΚΛΕΙΝΕΙΣ κιόλας, θα χρειαστούμε taskkill.")
    print("--- ✅ Το τεστ ολοκληρώθηκε ---")

if __name__ == "__main__":
    run_camera_test()