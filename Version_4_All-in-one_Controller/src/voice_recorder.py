import pyaudio
import wave
import os

class VoiceRecorder:
    def __init__(self):
        # Βασικές ρυθμίσεις ήχου
        self.chunk = 2048
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000 
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.is_recording = False
        
        # --- ΔΟΜΗ ΦΑΚΕΛΩΝ: command/recordings ---
        # Βρίσκουμε τη διαδρομή του αρχείου και πηγαίνουμε στη ρίζα του project
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Ορισμός διαδρομών
        self.base_dir = os.path.join(project_root, "command")
        self.rec_dir = os.path.join(self.base_dir, "recordings")
        
        # Δημιουργία των φακέλων αν δεν υπάρχουν
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            print(f"📁 Created base directory: {self.base_dir}")
            
        if not os.path.exists(self.rec_dir):
            os.makedirs(self.rec_dir)
            print(f"📁 Created recordings subdirectory: {self.rec_dir}")

    def start_recording(self):
        """Ξεκινάει την καταγραφή από το μικρόφωνο"""
        self.is_recording = True
        self.frames = []
        try:
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=1,  # <--- Προσοχή: Άλλαξέ το αν το ID του μικροφώνου σου είναι διαφορετικό
                frames_per_buffer=self.chunk
            )
            print(f"\n🔴 [RECORDING]: Started. Saving to {self.rec_dir}")
        except Exception as e:
            print(f"❌ [Mic Error]: {e}")
            self.is_recording = False

    def record_chunk(self):
        """Διαβάζει ένα κομμάτι ήχου από το stream"""
        if self.is_recording and self.stream:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"⚠️ [Stream Read Error]: {e}")

    def stop_recording(self):
        """Σταματάει την εγγραφή και αποθηκεύει το RAW αρχείο"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        
        # Κλείσιμο του stream
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        
        # Ορισμός ονόματος αρχείου: raw_command.wav
        file_path = os.path.join(self.rec_dir, "raw_command.wav")
        
        try:
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print(f"✅ [RECORDING]: Raw file saved at {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ [Save Error]: Could not write wav file. {e}")
            return None

    def __del__(self):
        """Καθαρισμός του PyAudio κατά την καταστροφή του αντικειμένου"""
        self.p.terminate()