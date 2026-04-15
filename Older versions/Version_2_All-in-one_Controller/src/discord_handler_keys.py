import keyboard

def handle_discord_shortcuts(command):
    if command == "DISCORD_MUTE":
        keyboard.send("ctrl+alt+shift+m")
    elif command == "DISCORD_DEAFEN":
        keyboard.send("ctrl+alt+shift+d")