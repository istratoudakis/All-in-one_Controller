import keyboard
import time

def handle_zoom(command):
    if command == "ZOOM_MUTE":
        keyboard.send("alt+a")
    elif command == "ZOOM_CAMERA":
        keyboard.send("alt+v")
    elif command == "ZOOM_HAND":
        keyboard.send("alt+y")
    elif command == "ZOOM_LEAVE":
        keyboard.send("alt+q")
        time.sleep(0.5)
        keyboard.send("enter")