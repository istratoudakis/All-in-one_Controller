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
        description = port.description.upper()
        if "CP210" in description or "CH340" in description or "USB SERIAL" in description:
            return port.device
    return None

def start_watching():
    # 📂 Καθορισμός διαδρομών
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bridge_script = os.path.join(current_dir, "serial_bridge.py")
    
    # Υπολογισμός της διαδρομής του .venv Python
    # Αν ο handler είναι μέσα στο src/, πάμε ένα φάκελο πίσω για να βρούμε το .venv
    project_root = os.path.dirname(current_dir) 
    venv_python = os.path.join(current_dir, "..", "..", ".venv", "Scripts", "python.exe")

    print(f"--- 🛡️ Universal Watcher Active ---")   
    print(f"Searching for ESP32...")
    print(f"VENV Interpreter: {venv_python}")

    while True:
        port = find_esp32_port()
        
        if port:
            print(f"✅ ESP32 detected on {port}! Launching bridge via VENV...")
            
            try:
                # Εκκίνηση του bridge χρησιμοποιώντας ΠΑΝΤΑ τον interpreter του .venv
                subprocess.Popen([venv_python, bridge_script, port], cwd=current_dir)
                
                # Αναμονή μέχρι να αποσυνδεθεί η συγκεκριμένη θύρα
                while any(p.device == port for p in serial.tools.list_ports.comports()):
                    time.sleep(2)
                
                print("❌ ESP32 disconnected. Scanning again...")
            except Exception as e:
                print(f"❌ Error launching bridge: {e}")
            
        time.sleep(1)

if __name__ == "__main__":
    start_watching()