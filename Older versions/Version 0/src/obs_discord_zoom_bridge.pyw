import obsws_python as obs
import serial
import time
import keyboard
import threading
import subprocess
import os
from pypresence import Client
import tkinter as tk
from tkinter import ttk

# ==========================================
# --- ΡΥΘΜΙΣΕΙΣ ---
# ==========================================
PORT = "COM3"
BAUD = 115200
CLIENT_ID = '1483485917221093519' # Από το Discord Developer Portal
OBS_PWD = "GKirg0ABORuhkUlZ"

status_state = {"mic": "LIVE", "deaf": "OFF"}

def is_process_running(process_name):
    try:
        output = subprocess.check_output('tasklist', creationflags=subprocess.CREATE_NO_WINDOW)
        return process_name.lower() in output.decode('utf-8', errors='ignore').lower()
    except:
        return False

# ==========================================
# --- DISCORD RPC THREAD (Αόρατο True Sync) ---
# ==========================================
def discord_rpc_thread():
    while True:
        if is_process_running("discord.exe"):
            try:
                rpc = Client(CLIENT_ID)
                rpc.start()
                print("✅ Discord RPC: Connected! (Running silently)")

                def voice_callback(data):
                    v = data.get('voice_settings', {})
                    status_state["mic"] = "MUTED" if v.get('mute') else "LIVE"
                    status_state["deaf"] = "ON" if v.get('deaf') else "OFF"
                    # Εδώ στο μέλλον μπορούμε να στείλουμε σήμα στο ESP32 για LED
                    # π.χ. ser.write(b"<LED:MIC_MUTE>\n")

                rpc.subscribe('VOICE_SETTINGS_UPDATE', voice_callback)
                
                while is_process_running("discord.exe"):
                    time.sleep(2)
            except Exception:
                time.sleep(5)
        else:
            time.sleep(2)

# Ξεκινάει στο παρασκήνιο, χωρίς να ανοίγει παράθυρα
threading.Thread(target=discord_rpc_thread, daemon=True).start()

# ==========================================
# --- GUI ΕΚΚΙΝΗΣΗΣ (Dashboard) ---
# ==========================================
def launch_apps_gui():
    root = tk.Tk()
    root.title("ESP32 Dashboard")
    root.geometry("300x260")
    root.attributes('-topmost', True)
    root.resizable(False, False)
    
    discord_var = tk.BooleanVar(value=not is_process_running("discord.exe"))
    obs_var = tk.BooleanVar(value=not is_process_running("obs64.exe"))
    zoom_var = tk.BooleanVar(value=False) # Προεπιλογή False για το Zoom
    
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Τι θέλεις να ανοίξεις;", font=("Segoe UI", 10, "bold")).pack(pady=10)
    
    # 3 Επιλογές πλέον
    ttk.Checkbutton(frame, text="Discord", variable=discord_var).pack(anchor="w", pady=5)
    ttk.Checkbutton(frame, text="OBS Studio", variable=obs_var).pack(anchor="w", pady=5)
    ttk.Checkbutton(frame, text="Zoom", variable=zoom_var).pack(anchor="w", pady=5)

    def start():
        d, o, z = discord_var.get(), obs_var.get(), zoom_var.get()
        root.destroy() # Εξαφανίζεται αμέσως το παράθυρο
        
        if d and not is_process_running("discord.exe"):
            path = os.path.join(os.environ.get('LOCALAPPDATA'), "Discord", "Update.exe")
            if os.path.exists(path): subprocess.Popen([path, "--processStart", "Discord.exe"])
        
        if o and not is_process_running("obs64.exe"):
            path = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
            if os.path.exists(path): 
                subprocess.Popen([path], cwd=r"C:\Program Files\obs-studio\bin\64bit")
        
        if z and not is_process_running("zoom.exe"):
            path = os.path.join(os.environ.get('APPDATA'), "Zoom", "bin", "Zoom.exe")
            if os.path.exists(path): 
                subprocess.Popen([path])
    
    ttk.Button(frame, text="ΕΚΚΙΝΗΣΗ", command=start).pack(pady=15)
    
    # Κεντράρισμα παραθύρου
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

# ==========================================
# --- MAIN LOOP ---
# ==========================================
print("🕵️ Περιμένω το ESP32...")
while True:
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.1)
        launch_apps_gui() # Ρωτάει τον χρήστη για τα 3 προγράμματα
        
        # Ανάλογα αν έχεις ανοιχτό το OBS τώρα, βγάλε το σχόλιο από την παρακάτω γραμμή:
        # cl = obs.ReqClient(host='localhost', port=4455, password=OBS_PWD) 
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                
                # DISCORD
                if "DISCORD_MUTE" in line: keyboard.send("ctrl+alt+shift+m")
                elif "DISCORD_DEAFEN" in line: keyboard.send("ctrl+alt+shift+d")
                
                # ZOOM
                elif "ZOOM_MUTE" in line: keyboard.send("alt+a")
                elif "ZOOM_CAMERA" in line: keyboard.send("alt+v")
                elif "ZOOM_HAND" in line: keyboard.send("alt+y")
                elif "ZOOM_LEAVE" in line:
                    keyboard.send("alt+q")
                    time.sleep(0.5)
                    keyboard.send("enter")
                    
            time.sleep(0.01)
    except:
        time.sleep(2)