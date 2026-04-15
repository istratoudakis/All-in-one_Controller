import os
import numpy as np
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment
import speech_recognition as sr

def preprocess_audio(input_path):
    try:
        # 1. Noise Reduction
        data, rate = sf.read(input_path)
        reduced_noise = nr.reduce_noise(y=data, sr=rate, prop_decrease=0.85)
        
        # 2. Οργάνωση φακέλου processed
        # Παίρνουμε τη διαδρομή του 'command' (ένα επίπεδο πάνω από το recordings)
        command_dir = os.path.dirname(os.path.dirname(input_path))
        processed_dir = os.path.join(command_dir, "processed")
        
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
            
        temp_path = os.path.join(processed_dir, "temp.wav")
        sf.write(temp_path, reduced_noise, rate)

        # 3. Normalization
        audio = AudioSegment.from_file(temp_path)
        normalized_audio = audio.normalize()
        
        # Τελική αποθήκευση στο command/processed/clean_command.wav
        final_path = os.path.join(processed_dir, "clean_command.wav")
        normalized_audio.export(final_path, format="wav")
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return final_path
    except Exception as e:
        print(f"❌ [DSP Error]: {e}")
        return None

def convert_voice_to_text(file_path):
    """
    Επεξεργάζεται τον ήχο και τον στέλνει στη Google.
    """
    if not os.path.exists(file_path):
        return None

    print("🎙️ [DSP] Ξεκινάει ο καθαρισμός σήματος...")
    if preprocess_audio(file_path):
        print("✨ [DSP] Ο ήχος καθαρίστηκε επιτυχώς.")
    
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            # Αποστολή στη Google (υποστηρίζει Ελληνικά και Αγγλικά)
            text = recognizer.recognize_google(audio_data, language="el-GR")
            print(f"🗣️ Google Heard: {text}")
            return text
        except sr.UnknownValueError:
            print("❓ [AI] Δεν κατάλαβα τι είπες.")
            return None
        except sr.RequestError as e:
            print(f"📡 [AI] Σφάλμα σύνδεσης με Google: {e}")
            return "ERROR_OFFLINE"