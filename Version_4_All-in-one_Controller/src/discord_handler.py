import keyboard

# Ξεκινάμε με το μικρόφωνο ανοιχτό
discord_state = {"mic": "LIVE", "deaf": "OFF"}

def _toggle_mic():
    discord_state["mic"] = "MUTED" if discord_state["mic"] == "LIVE" else "LIVE"
    print(f"🎧 [DISCORD UPDATE] Μικρόφωνο: {discord_state['mic']}")

def _toggle_deaf():
    discord_state["deaf"] = "ON" if discord_state["deaf"] == "OFF" else "OFF"
    print(f"🎧 [DISCORD UPDATE] Ακουστικά (Deafen): {discord_state['deaf']}")

def start_discord_rpc():
    """
    Αντί για το μπλοκαρισμένο API του Discord, 'κρυφακούμε' τα Hotkeys!
    Δουλεύει 100% offline και αστραπιαία.
    """
    try:
        # Ακούμε τα hotkeys που έχεις ρυθμίσει στο Discord (και τα στέλνει και το AI σου)
        keyboard.add_hotkey('ctrl+alt+shift+m', _toggle_mic)
        keyboard.add_hotkey('ctrl+alt+shift+d', _toggle_deaf)
        print("✅ Discord Tracker: ONLINE (Ακούει τα Hotkeys!)")
    except Exception as e:
        print(f"❌ Σφάλμα με τα Hotkeys: {e}")

def get_discord_state():
    return discord_state