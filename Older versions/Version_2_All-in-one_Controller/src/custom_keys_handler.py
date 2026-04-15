import webbrowser
import os

class CustomLinks:
    def __init__(self, links):
        self.links = links

    def open(self, command):
        idx = -1
        if command == "LINK_1": idx = 0
        elif command == "LINK_2": idx = 1
        elif command == "LINK_3": idx = 2

        if idx != -1 and self.links[idx]:
            target = self.links[idx]
            if target.lower().startswith(("http://", "https://", "www.")):
                webbrowser.open(target)
            else:
                try: os.startfile(target)
                except: pass