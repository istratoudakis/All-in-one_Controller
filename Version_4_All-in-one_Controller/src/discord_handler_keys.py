import keyboard

def handle_discord_shortcuts(command):
    if command == "DISCORD_MUTE":
        keyboard.send("ctrl+shift+m")
    elif command == "DISCORD_DEAFEN":
        keyboard.send("ctrl+shift+d")