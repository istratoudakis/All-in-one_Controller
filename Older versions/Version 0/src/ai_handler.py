import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
def hardcoded_fallback(text):
    """
    🛡️ Η ΕΣΧΑΤΗ ΓΡΑΜΜΗ ΑΜΥΝΑΣ: 
    Εμπλουτισμένο με "Stress Test" φράσεις για την παρουσίαση.
    """
    text = text.lower()
    
    # Λεξικό για να εντυπωσιάσεις τους καθηγητές ακόμα και OFFLINE
    fallbacks = {
        # --- Ακαδημαϊκά / Παρουσίαση ---
        "μάθημα": {"app_control": ["ZOOM_HAND", "ZOOM_CAMERA"], "camera": "TOGGLE", "feedback": "<ZOOM:READY><CAM:TOGGLE>"},
        "ξεκινάμε": {"app_control": ["OBS_START", "ZOOM_CAMERA"], "camera": "TOGGLE", "feedback": "<LIVE:START><CAM:ON>"},
        "παρουσίαση": {"boss_key": True, "volume": 0, "feedback": "<SYS:PRESENT_MODE>"},
        "εξέταση": {"mic_mute": True, "volume": 0, "feedback": "<EXAM:SILENCE>"},
        "τέλος": {"app_control": ["ZOOM_LEAVE", "OBS_STOP"], "feedback": "<SYS:GOODBYE>"},

        # --- Έλεγχος Ήχου (Slang & Expressions) ---
        "ησυχία": {"volume": 0, "mic_mute": True, "feedback": "<VOL:0><MIC:MUTE>"},
        "σκάσε": {"volume": 0, "feedback": "<VOL:0>"},
        "γκαζι": {"volume": 100, "feedback": "<VOL:100>"},
        "τέρμα": {"volume": 100, "feedback": "<VOL:100>"},
        "χαμήλωσε": {"volume": 20, "feedback": "<VOL:20>"},
        "φουλ": {"volume": 100, "feedback": "<VOL:100"},
        "κλείσε": {"volume": 0, "feedback": "<VOL:0"},

        # --- "Emergency" / Boss Key ---
        "αφεντικό": {"boss_key": True, "feedback": "<SYS:BOSS>"},
        "γυναίκα": {"boss_key": True, "feedback": "<SYS:BOSS>"},
        "μαμά": {"boss_key": True, "feedback": "<SYS:BOSS>"},
        "έρχεται": {"boss_key": True, "feedback": "<SYS:BOSS>"},
        "κρύψε": {"boss_key": True, "feedback": "<SYS:BOSS>"},

        # --- Media & Spotify ---
        "χάλια": {"spotify": "NEXT", "feedback": "<SPOT:NEXT>"},
        "βαρέθηκα": {"spotify": "NEXT", "feedback": "<SPOT:NEXT>"},
        "μουσική": {"spotify": "TOGGLE", "feedback": "<SPOT:PLAY>"},
        "σταμάτα": {"spotify": "TOGGLE", "feedback": "<SPOT:STOP>"},

        # --- Lifestyle / Context ---
        "gaming": {"app_control": ["DISCORD_MUTE"], "volume": 40, "feedback": "<MODE:GAMING>"},
        "ύπνο": {"volume": 0, "spotify": "TOGGLE", "boss_key": True, "feedback": "<SYS:SLEEP>"},
        "συγκεντρωθώ": {"volume": 10, "mic_mute": True, "feedback": "<MODE:FOCUS>"}
    }

    for key, data in fallbacks.items():
        if key in text:
            result = {
                "spotify": data.get("spotify", "NONE"),
                "volume": data.get("volume", None),
                "mic_mute": data.get("mic_mute", None),
                "boss_key": data.get("boss_key", False),
                "camera": data.get("camera", "NONE"),
                "app_control": data.get("app_control", ["NONE"]),
                "feedback": data.get("feedback", "<SYS:SAFE_MODE>")
            }
            print(f"[RESCUE]: Offline Match Found for '{key}'")
            return result
            
    return {
        "spotify": "NONE", "volume": None, "mic_mute": None,
        "boss_key": False, "camera": "NONE", "app_control": ["NONE"],
        "feedback": "<ERR:UNKNOWN_CONTEXT>"
    }

def quick_parse(text):
    """
    ⚡ ΕΝΙΣΧΥΜΕΝΟΣ LOCAL PARSER: Μαζεύει ΠΟΛΛΑΠΛΑ intents ταυτόχρονα.
    """
    text = text.lower()
    result = {
        "spotify": "NONE", "volume": None, "mic_mute": None,
        "boss_key": False, "camera": "NONE", "app_control": [], "feedback": []
    }
    found_something = False

    # 1. Volume Check
    match = re.search(r"(\d+)", text)
    if match and any(word in text for word in ["ένταση", "ένας", "volume", "στο", "βάλε"]):
        vol = int(match.group(1))
        if 0 <= vol <= 100:
            result["volume"] = vol
            result["feedback"].append(f"<VOL:{vol}>")
            found_something = True
    # Μέσα στο quick_parse (ai_handler.py)
    if any(word in text for word in ["φουλ", "full", "τερμα", "max"]):
        result["volume"] = 100  # <--- ΠΡΟΣΟΧΗ: Όχι "full", αλλά 100
        result["feedback"].append("<VOL:100>")
        found_something = True

    # 2. Camera Check (Ανεξάρτητο)
    if any(word in text for word in ["κάμερα", "camera"]) and not any(word in text for word in ["χέρι", "hand"]):
        result["camera"] = "TOGGLE"
        result["feedback"].append("<CAM:TOGGLE>")
        found_something = True

    # 3. Zoom Actions
    if "zoom" in text or any(word in text for word in ["χέρι", "hand", "σήκωσε"]):
        if any(word in text for word in ["χέρι", "hand", "σήκωσε"]):
            result["app_control"].append("ZOOM_HAND")
            result["feedback"].append("<ZOOM:HAND>")
            found_something = True
        if any(word in text for word in ["κάμερα", "camera", "άνοιξε", "κλείσε"]):
            result["app_control"].append("ZOOM_CAMERA")
            result["camera"] = "TOGGLE" 
            result["feedback"].append("<CAM:TOGGLE>")
            found_something = True

    # 4. Boss Key Check
    boss_words = ["σβήσε", "κρύψε", "παράθυρα", "αφεντικό", "boss", "έρχεται"]
    if any(word in text for word in boss_words):
        result["boss_key"] = True
        result["feedback"].append("<SYS:BOSS>")
        found_something = True

    # 5. Spotify Check
    if any(word in text for word in ["παύση", "σταμάτα", "σταματης", "pause", "stop"]):
        result["spotify"] = "TOGGLE"
        result["feedback"].append("<SPOT:STOP>")
        found_something = True
    elif any(word in text for word in ["επόμενο", "άλλαξε", "next", "τραγούδι"]):
        result["spotify"] = "NEXT"
        result["feedback"].append("<SPOT:NEXT>")
        found_something = True

    # 6. Mic Mute Check
    if any(word in text for word in ["σίγαση", "μικρόφωνο", "mute", "μουγκά"]):
        result["mic_mute"] = True
        result["feedback"].append("<MIC:MUTE>")
        found_something = True

    # 7. OBS Check
    if any(word in text for word in ["live", "stream", "obs", "εκπομπή"]):
        if any(word in text for word in ["ξεκίνησε", "άνοιξε", "start"]):
            result["app_control"].append("OBS_START")
            result["feedback"].append("<OBS:LIVE>")
            found_something = True
        elif any(word in text for word in ["κλείσε", "σταμάτα", "stop"]):
            result["app_control"].append("OBS_STOP")
            result["feedback"].append("<OBS:STOP>")
            found_something = True

    # 8. Special Shortcuts
    if any(word in text for word in ["δεν ακούω", "δεν ακούγεται", "γκαζι", "δυνάμωσε"]):
        result["volume"] = 100
        result["feedback"].append("<VOL:100>")
        found_something = True

    if found_something:
        if not result["app_control"]: result["app_control"] = ["NONE"]
        result["feedback"] = "".join(result["feedback"])
        return result
    return None

def parse_voice_command(user_text):
    if not user_text or user_text == "ERROR_OFFLINE":
        return hardcoded_fallback("error")

    # 🚀 ΒΗΜΑ 1: LOCAL PARSER
    quick = quick_parse(user_text)
    if quick:
        print(f"[DEBUG]: Local Match Found → {user_text}")
        return quick

    # ΒΗΜΑ 2: AI PROCESSING
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"[DEBUG]: Sending to AI → {user_text}")
        try:
            client = genai.Client(api_key=api_key)
            prompt = (
                f"Role: Smart Controller. Command: '{user_text}'. "
                "Output: ONLY raw JSON. Structure: { spotify, volume, mic_mute, boss_key, camera, app_control: LIST, feedback: TAGS }. "
                "CRITICAL: app_control MUST be a LIST. feedback MUST use tags like <VOL:val>, <OBS:LIVE>, <ZOOM:HAND>."
            )

            models_to_try = [
                "models/gemini-2.0-flash",
                "models/gemini-1.5-flash-latest",
                "models/gemini-flash-lite-latest"
            ]

            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type='application/json',
                            http_options={'timeout': 20000}
                        )
                    )
                    parsed = json.loads(response.text.strip())
                    # Defaults
                    defaults = {"spotify": "NONE", "app_control": ["NONE"], "feedback": "<SYS:OK>"}
                    for k, v in defaults.items(): parsed.setdefault(k, v)
                    return parsed
                except Exception as e:
                    print(f"[DEBUG]: Model {model_name} failed: {e}")
                    continue
        except Exception as e:
            print(f"[CRITICAL AI ERROR]: {e}")

    # ΒΗΜΑ 3: FAILSAFE (Αν όλα αποτύχουν)
    print("[WARNING]: AI failed or Quota exhausted. Using Hardcoded Fallback.")
    return hardcoded_fallback(user_text)