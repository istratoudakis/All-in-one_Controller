import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
import unicodedata

load_dotenv()

def normalize_greek(text):
    text = text.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def hardcoded_fallback(text):
    """
    🛡️ Η ΕΣΧΑΤΗ ΓΡΑΜΜΗ ΑΜΥΝΑΣ: 
    Χρησιμοποιεί Stemming για να λειτουργεί ακόμα και offline με παραλλαγές λέξεων.
    """
    text = normalize_greek(text)
    
    # Λεξικό με ρίζες λέξεων (Stemming) για μέγιστη κάλυψη
    fallbacks = {
        # --- Ακαδημαϊκά / Zoom / Παρουσίαση ---
        "μαθημα": {"app_control": ["ZOOM_HAND", "ZOOM_CAMERA"], "camera": "TOGGLE", "feedback": "<ZOOM:READY><CAM:TOGGLE>"},
        "παρουσιασ": {"boss_key": True, "volume": 0, "feedback": "<SYS:PRESENT_MODE>"},
        "εξετασ": {"mic_mute": True, "volume": 0, "feedback": "<EXAM:SILENCE>"},
        "τελος": {"app_control": ["ZOOM_LEAVE", "OBS_STOP"], "feedback": "<SYS:GOODBYE>"},
        "τουρμπο": {"volume": 100, "app_control": ["MAX_PERFORMANCE"], "feedback": "<SYS:TURBO>"},
        "χερ": {"app_control": ["ZOOM_HAND"], "feedback": "<ZOOM:HAND>"},
        "σηκωσ": {"app_control": ["ZOOM_HAND"], "feedback": "<ZOOM:HAND>"},
        "hand": {"app_control": ["ZOOM_HAND"], "feedback": "<ZOOM:HAND>"},
        "οθον": {"app_control": ["SCREEN_SHARE"], "feedback": "<SYS:SCREEN>"},
        "μοιρασ": {"app_control": ["SCREEN_SHARE"], "feedback": "<SYS:SCREEN>"},

        # --- Έλεγχος Ήχου ---
        "ησυχ": {"volume": 0, "mic_mute": True, "feedback": "<VOL:0><MIC:MUTE>"},
        "σκασε": {"volume": 0, "feedback": "<VOL:0>"},
        "γκαζ": {"volume": 100, "feedback": "<VOL:100>"},
        "τερμα": {"volume": 100, "feedback": "<VOL:100>"},
        "χαμηλ": {"volume": "-10", "feedback": "<VOL:DOWN>"},
        "δυναμ": {"volume": "+10", "feedback": "<VOL:UP>"},

        # --- Emergency / Boss Key / Discord ---
        "αφεντ": {"boss_key": True, "feedback": "<SYS:BOSS>"},
        "ερχετ": {"boss_key": True, "feedback": "<SYS:BOSS>"},
        "κρυψ": {"boss_key": True, "feedback": "<SYS:BOSS>"},
        "κουφ": {"app_control": ["DISCORD_DEAFEN"], "feedback": "<SYS:DEAFEN>"},
        "ακουστ": {"app_control": ["DISCORD_DEAFEN"], "feedback": "<SYS:DEAFEN>"},
        "deafen": {"app_control": ["DISCORD_DEAFEN"], "feedback": "<SYS:DEAFEN>"},
        "λειπ": {"app_control": ["BRB_MODE"], "boss_key": True, "feedback": "<SYS:BRB>"},
        "brb": {"app_control": ["BRB_MODE"], "boss_key": True, "feedback": "<SYS:BRB>"},

        # --- Media / Spotify ---
        "χαλια": {"spotify": "NEXT", "feedback": "<SPOT:NEXT>"},
        "μουσικ": {"spotify": "TOGGLE", "feedback": "<SPOT:PLAY>"},
        "σταματ": {"spotify": "TOGGLE", "feedback": "<SPOT:STOP>"},
        "επομε": {"spotify": "NEXT", "feedback": "<SPOT:NEXT>"},
        "τραγου": {"spotify": "NEXT", "feedback": "<SPOT:NEXT>"},
        "προηγουμ": {"spotify": "PREV", "feedback": "<SPOT:PREV>"},
        "πριν": {"spotify": "PREV", "feedback": "<SPOT:PREV>"},
        "αλλαξ": {"spotify": "NEXT", "feedback": "<SPOT:NEXT>"},

        # --- OBS / On Air ---
        "αερα": {"app_control": ["OBS_START"], "feedback": "<OBS:ON_AIR>"},
        "air": {"app_control": ["OBS_START"], "feedback": "<OBS:ON_AIR>"},
        "live": {"app_control": ["OBS_START"], "feedback": "<OBS:ON_AIR>"}
    }

    for key, data in fallbacks.items():
        if key in text:
            # Δημιουργία πλήρους αντικειμένου για αποφυγή KeyErrors
            return {
                "spotify": data.get("spotify", "NONE"),
                "volume": data.get("volume", None),
                "mic_mute": data.get("mic_mute", None),
                "boss_key": data.get("boss_key", False),
                "camera": data.get("camera", "NONE"),
                "app_control": data.get("app_control", ["NONE"]),
                "feedback": data.get("feedback", "<SYS:SAFE_MODE>")
            }
            
    return {
        "spotify": "NONE", "volume": None, "mic_mute": None,
        "boss_key": False, "camera": "NONE", "app_control": ["NONE"],
        "feedback": "<ERR:UNKNOWN_CONTEXT>"
    }

def quick_parse(text):
    """
    ⚡ ΕΝΙΣΧΥΜΕΝΟΣ LOCAL PARSER: 
    Χρησιμοποιεί Stemming και Smart Word Count Routing.
    """
    text = normalize_greek(text)
    words_list = text.split()

    # Αν η εντολή είναι σύνθετη (> 6 λέξεις), την αφήνουμε στο AI
    if len(words_list) > 9:
        return None
    
    parts = re.split(r'\s(?:και|and|μετα|τοτε)\s', text)

    result = {
        "spotify": "NONE", "volume": None, "mic_mute": None,
        "boss_key": False, "camera": "NONE", "app_control": [], "feedback": []
    }
    found_something = False

    for part in parts:
        part = part.strip()
        if not part: continue

        # 1. Volume Check (Absolute & Relative)
        match = re.search(r"(\d+)", part)
        if match and any(word in part for word in ["εντασ", "vol", "βαλε", "στο"]):
            vol = int(match.group(1))
            if 0 <= vol <= 100:
                result["volume"] = vol
                result["feedback"].append(f"<VOL:{vol}>")
                found_something = True

        if any(word in part for word in ["δυναμ", "ανεβασ", "ανεβαζ", "γκαζ", "δυνατα"]):
            result["volume"] = "+10"
            result["feedback"].append("<VOL:UP>")
            found_something = True
        elif any(word in part for word in ["χαμηλ", "κατεβ", "σιγα", "σιγο"]):
            result["volume"] = "-10"
            result["feedback"].append("<VOL:DOWN>")
            found_something = True
        
        if any(word in part for word in ["φουλ", "full", "τερμα", "max"]):
            result["volume"] = 100
            result["feedback"].append("<VOL:100>")
            found_something = True

        # 2. Camera Check
        if any(word in part for word in ["καμερ", "cam"]) and "χερι" not in text:
            result["camera"] = "TOGGLE"
            result["feedback"].append("<CAM:TOGGLE>")
            found_something = True

        # 3. Zoom / Screen Share / Hand (Stemming: χερ, σηκωσ, οθον)
        if any(word in part for word in ["χερ", "σηκωσ", "hand"]):
            result["app_control"].append("ZOOM_HAND")
            result["feedback"].append("<ZOOM:HAND>")
            found_something = True
        
        if any(word in part for word in ["οθον", "μοιρασ", "screen", "share"]):
            result["app_control"].append("SCREEN_SHARE")
            result["feedback"].append("<SYS:SCREEN>")
            found_something = True

        # 4. Deafen / BRB / Boss Key (Stemming: κουφ, λειπ, σβησ)
        if any(word in part for word in ["κουφ", "ακουστ", "deafen"]):
            result["app_control"].append("DISCORD_DEAFEN")
            result["feedback"].append("<SYS:DEAFEN>")
            found_something = True

        if any(word in part for word in ["λειπ", "γυριζ", "brb", "διαλειμ"]):
            result["app_control"].append("BRB_MODE")
            result["boss_key"] = True
            result["feedback"].append("<SYS:BRB>")
            found_something = True

        if any(word in part for word in ["σβησ", "κρυψ", "παραθυρ", "αφεντ", "boss", "ερχετ"]):
            result["boss_key"] = True
            result["feedback"].append("<SYS:BOSS>")
            found_something = True

        # 5. On Air / OBS (Stemming: εκπομπ, αερα, air)
        if any(word in part for word in ["live", "obs", "εκπομπ", "αερα", "air"]):
            if any(word in part for word in ["ξεκινησ", "ανοιξ", "start", "on"]):
                result["app_control"].append("OBS_START")
                result["feedback"].append("<OBS:ON_AIR>")
                found_something = True
            elif any(word in part for word in ["κλεισ", "σταματ", "stop", "off"]):
                result["app_control"].append("OBS_STOP")
                result["feedback"].append("<OBS:OFF>")
                found_something = True

        # 6. Media Logic (Spotify vs Global Media)
        # Ξεχωρίζουμε αν ο χρήστης αναφέρθηκε σε Spotify/Τραγούδι ή σε Βίντεο/Media
        is_spotify = any(word in part for word in ["spotify", "μουσικ", "τραγου"])
        is_global_media = any(word in part for word in ["βιντεο", "ταινι", "media", "youtube", "yt"])

        if any(word in part for word in ["επομε", "next", "αλλαξ"]):
            result["spotify"] = "NEXT"
            result["feedback"].append("<SPOT:NEXT>")
            found_something = True
        elif any(word in part for word in ["προηγουμ", "πριν", "πισω", "prev"]):
            result["spotify"] = "PREV"
            result["feedback"].append("<SPOT:PREV>")
            found_something = True
        elif any(word in part for word in ["παυσ", "σταματ", "stop", "pause", "παιξε"]):
            if is_global_media:
                result["app_control"].append("MEDIA_TOGGLE")
                result["feedback"].append("<MEDIA:TOGGLE>")
            else:
                # Default στο Spotify αν δεν διευκρινίσει
                result["spotify"] = "TOGGLE"
                result["feedback"].append("<SPOT:TOGGLE>")
            found_something = True

        # 7. Mic Mute Check
        if any(word in part for word in ["σιγασ", "μικροφ", "mute", "μουγκ"]):
            result["mic_mute"] = True
            result["feedback"].append("<MIC:MUTE>")
            found_something = True

    if found_something:
        if not result["app_control"]: 
            result["app_control"] = ["NONE"]
        
        # Αφαίρεση διπλών tags από το feedback (χρήση dict keys για διατήρηση σειράς)
        result["feedback"] = "".join(dict.fromkeys(result["feedback"]))
        return result
    
    return None

def parse_voice_command(user_text):
    """
    Κεντρική συνάρτηση διαχείρισης φωνητικών εντολών.
    """
    if not user_text or user_text == "ERROR_OFFLINE":
        return hardcoded_fallback("error")

    # 🚀 ΒΗΜΑ 1: Local Parser (Γρήγορο Ταίριασμα)
    quick = quick_parse(user_text)
    if quick:
        return quick

    # 🚀 ΒΗΜΑ 2: AI Processing (Dual Key Failover)
    # Προσέχουμε τα ονόματα των μεταβλητών και τις εσοχές (indents)
    api_keys_list = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
    
    prompt = (
    f"Context: High-end PC Voice Controller. User said: '{user_text}'. "
    "Task: Extract actions into JSON. Rules: "
    "1. 'volume': If user mentions a number (e.g., 'στο 30'), set it to that integer. If 'up/down', use '+10' or '-10'. "
    "2. 'app_control': If it's about Zoom/Teams/Meet, use 'ZOOM_HAND' for raising hand, 'SCREEN_SHARE' for sharing. "
    "3. 'feedback': Create a short tag like <VOL:30> or <ZOOM:HAND> for the ESP32 screen. "
    "Return ONLY raw JSON, no markdown."
    )

    # Ξεκινάει το Loop των Keys
    for current_key in api_keys_list:
        if not current_key:
            continue  # Πάει στο επόμενο key αν αυτό είναι κενό
        
        try:
            client = genai.Client(api_key=current_key)
            models_to_try = ["models/gemini-2.0-flash", "models/gemini-1.5-flash-latest"]
            
            # Εσωτερικό Loop για τα μοντέλα
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type='application/json')
                    )
                    
                    raw_json = response.text.strip()
                    if raw_json.startswith("```"):
                        raw_json = re.sub(r'^```json\s*|```$', '', raw_json, flags=re.MULTILINE)
                    
                    parsed = json.loads(raw_json)
                    
                    # Normalization
                    if "spotify" in parsed: 
                        parsed["spotify"] = str(parsed["spotify"]).upper()
                    
                    # Defaults
                    defaults = {"spotify": "NONE", "app_control": ["NONE"], "feedback": "<SYS:OK>"}
                    for k, v in defaults.items(): 
                        parsed.setdefault(k, v)
                    
                    return parsed # ✅ ΕΔΩ ΤΕΛΕΙΩΝΟΥΝ ΟΛΑ ΑΝ ΠΕΤΥΧΕΙ
                
                except Exception as e:
                    if "429" in str(e):
                        print(f"⚠️ Quota Full για το μοντέλο {model_name}. Δοκιμάζω το επόμενο...")
                        # Αν είναι το τελευταίο μοντέλο αυτού του Key, θα βγει από το inner loop
                        continue 
                    print(f"❌ Σφάλμα μοντέλου: {e}")
                    continue

        except Exception as e:
            print(f"❌ Σφάλμα με το API Key: {e}")
            continue # Πάει στο επόμενο API Key της λίστας

    # 🚀 ΒΗΜΑ 3: Failsafe Fallback (Αν βγει από όλα τα loops χωρίς να κάνει return)
    return hardcoded_fallback(user_text)