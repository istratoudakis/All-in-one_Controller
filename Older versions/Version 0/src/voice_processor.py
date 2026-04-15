import speech_recognition as sr

def convert_voice_to_text(file_path):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300 
    
    try:
        with sr.AudioFile(file_path) as source:
            # Προσαρμογή στον θόρυβο
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            
            # Χρήση Google Speech Recognition
            text = recognizer.recognize_google(audio_data, language="el-GR")
            print(f"Recognized: {text}")
            return text
            
    except sr.RequestError:
        # ΚΡΙΣΙΜΟ: Σφάλμα σύνδεσης στο Internet
        print("[SYSTEM ERROR]: No internet connection for Speech API.")
        return "ERROR_OFFLINE"
        
    except sr.UnknownValueError:
        print("[SYSTEM]: Speech Recognition could not understand audio.")
        return None
        
    except Exception as e:
        print(f"[SYSTEM ERROR]: {e}")
        return None