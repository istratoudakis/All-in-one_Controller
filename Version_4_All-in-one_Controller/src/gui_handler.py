import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import webbrowser
import json
import sys

# --- ΝΕΑ IMPORTS ΓΙΑ ΤΟ CALIBRATION ---
import numpy as np
import pyaudio
from pc_controls import set_mic_volume # <--- ΠΡΟΣΘΗΚΗ: Σύνδεση με το Hardware Gain
# --------------------------------------

# ==========================================
# --- ΑΠΟΛΥΤΗ ΔΙΑΔΡΟΜΗ ΓΙΑ ΤΟ JSON ---
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR) # Ο κεντρικός φάκελος (ένα επίπεδο πίσω)
CONFIG_FILE = os.path.join(BASE_DIR, "custom_buttons.json")

# ==========================================
# --- MIC CALIBRATION ΛΟΓΙΚΗ (DIRECT PYAUDIO) ---
# ==========================================
def calibrate_mic():
    print("\n🎙️ Παρακαλώ μείνετε σιωπηλοί για 3 δευτερόλεπτα (Noise Calibration)...")
    try:
        # Ρυθμίσεις Καταγραφής (1 Κανάλι, 16000Hz, 3 Δευτερόλεπτα)
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 3

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []
        # Καταγραφή των δεδομένων του μικροφώνου στη μνήμη
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.int16))

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Υπολογισμός του θορύβου (RMS)
        raw_data = np.hstack(frames).astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(raw_data**2)))
        
        # Αποθήκευση στο αρχείο για το AI
        calib_data = {"ambient_noise_level": rms}
        with open(os.path.join(BASE_DIR, "noise_profile.json"), "w", encoding="utf-8") as f:
            json.dump(calib_data, f)
            
        # --- ΠΡΟΣΘΗΚΗ: Ρύθμιση Hardware Gain (0-100) βάσει θορύβου ---
        if rms < 0.005:   target_gain = 95  # Πολύ ησυχία
        elif rms < 0.02:  target_gain = 80  # Κανονικό δωμάτιο
        elif rms < 0.08:  target_gain = 65  # Κάποια φασαρία
        else:             target_gain = 50  # Πολύς θόρυβος
        
        set_mic_volume(target_gain) # Ενημέρωση του slider των Windows
        # -----------------------------------------------------------

        target_volume = 58981 if rms < 0.05 else 39321
        
        # Χρήση του NirCmd από τον κεντρικό φάκελο
        nircmd_path = os.path.join(ROOT_DIR, "nircmd.exe")
        
        if os.path.exists(nircmd_path):
            subprocess.run([nircmd_path, "setsysvolume", str(target_volume), "default_record"], shell=True)
            print("🎛️ Η ένταση ρυθμίστηκε μέσω NirCmd!")
        else:
            print(f"⚠️ Το nircmd.exe δεν βρέθηκε στη διαδρομή: {nircmd_path}")
            
        print(f"✅ Το μικρόφωνο ρυθμίστηκε! (RMS: {rms:.5f}) -> Gain: {target_gain}%")
        messagebox.showinfo("Calibration Complete", f"Το μικρόφωνο ρυθμίστηκε επιτυχώς!\nΜέτρηση Θορύβου: {rms:.5f}\nΈνταση Windows: {target_gain}%")
    except Exception as e:
        print(f"❌ Σφάλμα: {e}")
        messagebox.showerror("Calibration Error", f"Σφάλμα κατά το calibration:\n{e}")

# ==========================================
# --- ΛΟΓΙΚΗ ΑΝΑΓΝΩΡΙΣΗΣ & ΣΩΣΙΜΑΤΟΣ ---
# ==========================================

def is_process_running(process_name):
    try:
        output = subprocess.check_output('tasklist', creationflags=subprocess.CREATE_NO_WINDOW)
        return process_name.lower() in output.decode('utf-8', errors='ignore').lower()
    except:
        return False

def generate_name_from_content(text):
    text = text.strip().replace('"', '') 
    if not text: 
        return ""
        
    if text.lower().startswith(("http://", "https://", "www.")):
        known_sites = {
            "youtube": "YouTube", 
            "google": "Google", 
            "reddit": "Reddit", 
            "discord": "Discord", 
            "spotify": "Spotify", 
            "twitch": "Twitch"
        }
        for key, val in known_sites.items():
            if key in text.lower(): 
                return val
        return "Ιστοσελίδα"
    else:
        try: 
            return os.path.splitext(os.path.basename(text))[0].capitalize()
        except: 
            return "Πρόγραμμα"

def bind_greek_shortcuts(widget):
    def handle_shortcuts(event):
        if event.state & 4: 
            if event.keycode == 86: 
                widget.event_generate('<<Paste>>')
                return 'break'
            elif event.keycode == 67: 
                widget.event_generate('<<Copy>>')
                return 'break'
            elif event.keycode == 88: 
                widget.event_generate('<<Cut>>')
                return 'break'
            elif event.keycode == 65: 
                widget.select_range(0, tk.END)
                return 'break'
    widget.bind('<Key>', handle_shortcuts, add="+")

# ==========================================
# --- ΚΥΡΙΟ ΓΡΑΦΙΚΟ ΠΕΡΙΒΑΛΛΟΝ ---
# ==========================================

def launch_apps_gui():
    root = tk.Tk()
    root.title("ESP32 Dashboard")
    root.attributes('-topmost', True)
    root.resizable(False, False)
    
    user_choices = {
        "discord": False, 
        "obs": False, 
        "zoom": False, 
        "spotify": False, 
        "links": ["", "", ""], 
        "dev_mode": False
    }
    
    frame = ttk.Frame(root, padding="15")
    frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="ESP32 Συνδέθηκε!", font=("Segoe UI", 11, "bold")).pack(pady=(0, 10))
    
    # --- 1. ΣΤΑΝΤΑΡ ΕΦΑΡΜΟΓΕΣ ---
    apps_frame = ttk.Frame(frame)
    apps_frame.pack(fill="x")
    
    discord_var = tk.BooleanVar(value=not is_process_running("discord.exe"))
    obs_var = tk.BooleanVar(value=not is_process_running("obs64.exe"))
    zoom_var = tk.BooleanVar(value=False) 
    spotify_var = tk.BooleanVar(value=not is_process_running("spotify.exe"))
    
    ttk.Checkbutton(apps_frame, text="Discord", variable=discord_var).pack(anchor="w", pady=2)
    ttk.Checkbutton(apps_frame, text="OBS Studio", variable=obs_var).pack(anchor="w", pady=2)
    ttk.Checkbutton(apps_frame, text="Zoom", variable=zoom_var).pack(anchor="w", pady=2)
    ttk.Checkbutton(apps_frame, text="Spotify", variable=spotify_var).pack(anchor="w", pady=2)

    custom_apps_display_frame = ttk.Frame(frame)
    custom_apps_display_frame.pack(fill="x", pady=(5, 0))

    top_rows = {}
    custom_cbs = {}
    custom_vars = {}
    name_vars = []
    link_entries = []

    def save_config():
        data = {"slots": []}
        for idx in range(len(name_vars)):
            path_val = link_entries[idx].get().strip()
            if path_val:
                data["slots"].append({
                    "name": name_vars[idx].get(),
                    "path": path_val,
                    "checked": custom_vars[idx].get() if idx in custom_vars else True
                })
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return {"slots": []}

    # --- 2. CUSTOM BUTTONS ΣΥΡΤΑΡΙ ---
    links_frame = ttk.Frame(frame)
    
    header_frame = ttk.Frame(links_frame)
    header_frame.pack(fill="x", pady=(15, 5))
    ttk.Label(header_frame, text="URLs ή Προγράμματα:", font=("Segoe UI", 9, "bold")).pack(side="left")
    
    def show_help():
        help_text = (
            "Πώς να ρυθμίσετε τα Custom Buttons:\n\n"
            "🌐 Για Ιστοσελίδα: Επικόλληση το URL.\n"
            "🖥️ Για Πρόγραμμα: Επικόλληση τη διαδρομή.\n\n"
            "💡 ΕΞΥΠΝΟ ΤΡΙΚ:\n"
            "1. 'Shift' + 'Δεξί Κλικ' στο εικονίδιο.\n"
            "2. 'Αντιγραφή ως διαδρομής'.\n"
            "3. Επικόλληση (Ctrl+V) εδώ!\n\n"
            "✅ Πατήστε ✅ για επιβεβαίωση!"
        )
        messagebox.showinfo("Need Help? - Οδηγίες", help_text)

    ttk.Button(header_frame, text="❓ Help", command=show_help, width=8).pack(side="right")

    slots_container = ttk.Frame(links_frame)
    slots_container.pack(fill="x")

    def auto_resize():
        root.update_idletasks()
        root.geometry(f"460x{root.winfo_reqheight()}")

    def create_top_checkbox(idx, name, path, is_checked=True):
        if idx in top_rows: 
            return
            
        row = ttk.Frame(custom_apps_display_frame)
        row.pack(fill="x", pady=1)
        top_rows[idx] = row
        
        c_var = tk.BooleanVar(value=is_checked)
        custom_vars[idx] = c_var
        
        cb = ttk.Checkbutton(row, text=name, variable=c_var)
        cb.pack(side="left")
        custom_cbs[idx] = cb
        
        def delete_slot():
            row.destroy()
            del top_rows[idx]
            del custom_vars[idx]
            name_vars[idx].set("")
            link_entries[idx].delete(0, tk.END)
            save_config()
            auto_resize()
            
        ttk.Button(row, text="🗑️", width=3, command=delete_slot).pack(side="right")
        
        c_var.trace_add("write", lambda *args: save_config())

    def add_slot():
        idx = len(name_vars)
        if idx < 3:
            slot_frame = ttk.Frame(slots_container)
            slot_frame.pack(fill="x", pady=5)
            
            ttk.Label(slot_frame, text=f"Slot {idx+1}:", font=("Segoe UI", 8)).pack(anchor="w")
            
            row = ttk.Frame(slot_frame)
            row.pack(fill="x")
            
            nv = tk.StringVar()
            name_vars.append(nv)
            
            en = ttk.Entry(row, textvariable=nv, width=12)
            en.pack(side="left", padx=(0, 5))
            
            el = ttk.Entry(row, width=30)
            el.pack(side="left", fill="x", expand=True)
            link_entries.append(el)
            
            def confirm():
                path = el.get().strip().replace('"', '')
                if path:
                    if not nv.get().strip(): 
                        nv.set(generate_name_from_content(path))
                    
                    app_name = nv.get().strip().lower()
                    if app_name in ["discord", "obs", "obs studio", "zoom", "spotify"]:
                        messagebox.showwarning("Προσοχή!", f"Η εφαρμογή '{nv.get()}' υπάρχει ήδη στις βασικές επιλογές (πάνω-πάνω)!")
                        return 
                        
                    create_top_checkbox(idx, nv.get(), path, True)
                    save_config()
                    auto_resize()
            
            ttk.Button(row, text="✅", command=confirm, width=3).pack(side="left", padx=(5, 0))
            
            bind_greek_shortcuts(en)
            bind_greek_shortcuts(el)
            
            def update_cb_name(*args):
                if idx in custom_cbs:
                    custom_cbs[idx].config(text=nv.get())
                save_config()
                
            nv.trace_add("write", update_cb_name)
            
            auto_resize()
            
            if len(name_vars) == 3: 
                btn_add.pack_forget()

    btn_add = ttk.Button(links_frame, text="➕ Προσθήκη Slot", command=add_slot)
    
    saved_config = load_config()
    saved_data = saved_config.get("slots", [])
    
    if isinstance(saved_data, dict):
        saved_data = list(saved_data.values())
    
    if not saved_data:
        add_slot() 
    else:
        for i, s in enumerate(saved_data):
            add_slot()
            name_vars[i].set(s.get("name", ""))
            link_entries[i].insert(0, s.get("path", ""))
            create_top_checkbox(i, s.get("name", ""), s.get("path", ""), s.get("checked", True))
            
        if len(saved_data) < 3:
            btn_add.pack(pady=10) 

    # --- 3. BOTTOM FRAME (ΝΕΟ LAYOUT) ---
    bottom_frame = ttk.Frame(frame)
    bottom_frame.pack(side="bottom", fill="x", pady=(15, 0))
    
    def toggle_custom():
        if links_frame.winfo_viewable(): 
            links_frame.pack_forget()
        else:
            bottom_frame.pack_forget()
            links_frame.pack(fill="x")
            bottom_frame.pack(fill="x")
            if len(name_vars) < 3: 
                btn_add.pack(pady=10)
        auto_resize()

    # Υπο-frame 1: Για Custom Buttons & Mic Calibration στην ίδια γραμμή
    row1_frame = ttk.Frame(bottom_frame)
    row1_frame.pack(fill="x", pady=(0, 5))
    
    ttk.Button(row1_frame, text="⚙️ Custom Buttons", command=toggle_custom).pack(side="left")
    ttk.Button(row1_frame, text="🎙️ Mic Calibration", command=calibrate_mic).pack(side="right")

    # Υπο-frame 2: Για Dev Console διακριτικά από κάτω δεξιά
    row2_frame = ttk.Frame(bottom_frame)
    row2_frame.pack(fill="x", pady=(0, 15))
    
    dev_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(row2_frame, text="🛠️ Dev Console", variable=dev_var).pack(side="right")

    def start():
        save_config()
        
        user_choices["discord"] = discord_var.get()
        user_choices["obs"] = obs_var.get()
        user_choices["zoom"] = zoom_var.get()
        user_choices["spotify"] = spotify_var.get()
        user_choices["dev_mode"] = dev_var.get()
        
        collected_links = [e.get().strip().replace('"', '') for e in link_entries]
        
        while len(collected_links) < 3: 
            collected_links.append("")
            
        user_choices["links"] = collected_links
        
        root.destroy()
        
        if user_choices["discord"] and not is_process_running("discord.exe"):
            path = os.path.join(os.environ.get('LOCALAPPDATA'), "Discord", "Update.exe")
            if os.path.exists(path): subprocess.Popen([path, "--processStart", "Discord.exe"])
        
        if user_choices["obs"] and not is_process_running("obs64.exe"):
            path = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
            if os.path.exists(path): subprocess.Popen([path], cwd=r"C:\Program Files\obs-studio\bin\64bit")
        
        if user_choices["zoom"] and not is_process_running("zoom.exe"):
            path = os.path.join(os.environ.get('APPDATA'), "Zoom", "bin", "Zoom.exe")
            if os.path.exists(path): subprocess.Popen([path])

        if user_choices["spotify"] and not is_process_running("spotify.exe"):
            spotify_path = os.path.join(os.environ.get('APPDATA'), "Spotify", "Spotify.exe")
            if os.path.exists(spotify_path): subprocess.Popen([spotify_path])
            else:
                try: os.startfile("spotify:")
                except: pass
            
        for idx in top_rows:
            if custom_vars[idx].get(): 
                link_to_run = collected_links[idx]
                if link_to_run:
                    if link_to_run.lower().startswith(("http://", "https://", "www.")): webbrowser.open(link_to_run)
                    else: os.startfile(link_to_run)

    # Το κεντρικό, μεγάλο κουμπί Εκκίνησης στο κάτω μέρος
    start_btn = tk.Button(bottom_frame, text="🚀 ΕΚΚΙΝΗΣΗ", command=start, bg="#007ACC", fg="white", font=("Segoe UI", 12, "bold"), padx=15, pady=5)
    start_btn.pack(anchor="center")
    
    def on_closing():
        save_config()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)

    auto_resize()
    x = (root.winfo_screenwidth() // 2) - (230)
    y = (root.winfo_screenheight() // 2) - (root.winfo_reqheight() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()
    return user_choices

if __name__ == "__main__":
    launch_apps_gui()