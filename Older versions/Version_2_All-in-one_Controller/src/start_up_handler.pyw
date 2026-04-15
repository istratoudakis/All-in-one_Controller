import serial.tools.list_ports
import time
import subprocess
import os
import sys

def find_esp32_port():
    """🔍 Ψάχνει αυτόματα σε όλες τις θύρες για συσκευή USB Serial (ESP32)"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Οι περισσότεροι ESP32 χρησιμοποιούν CP210x ή CH340 chipsets
        if "CP210" in port.description or "CH340" in port.description or "USB Serial" in port.description:
            return port.device
    return None

def start_watching():
    # 📂 Δυναμικό μονοπάτι: Παίρνει τον φάκελο στον οποίο βρίσκεται ΑΥΤΟ το script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bridge_script = os.path.join(current_dir, "serial_bridge.py")
    
    print(f"--- 🛡️ Universal Watcher Active ---")
    print(f"Looking for ESP32 in any COM port...")

    while True:
        port = find_esp32_port()
        
        if port:
            print(f"✅ ESP32 detected on {port}! Launching bridge...")
            
            # Εκκίνηση του bridge_script περνώντας τη θύρα ως επιχείρημα (argument)
            # Χρησιμοποιούμε sys.executable για να τρέξει με τον ίδιο Python interpreter
            subprocess.Popen([sys.executable, bridge_script, port], cwd=current_dir)
            
            # Αναμονή μέχρι να αποσυνδεθεί
            while port in [p.device for p in serial.tools.list_ports.comports()]:
                time.sleep(2)
                
            print("❌ ESP32 disconnected. Scanning again...")
            
        time.sleep(1)

if __name__ == "__main__":
    start_watching()