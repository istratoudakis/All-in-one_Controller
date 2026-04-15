import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Φόρτωση ρυθμίσεων
load_dotenv()

def get_spotify_client():
    scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_spotify_detailed_data():
    """
    Επιστρέφει 4 διαφορετικά strings σύμφωνα με το πρωτόκολλο <KEY:VALUE>
    """
    try:
        sp = get_spotify_client()
        pb = sp.current_playback()

        if pb and pb['item']:
            track = pb['item']
            
            # 1. Name - Artist
            name_artist = f"{track['name']} - {track['artists'][0]['name']}"
            
            # Μετατροπή ms σε mm:ss για ευκολία
            def format_time(ms):
                minutes = int((ms / (1000 * 60)) % 60)
                seconds = int((ms / 1000) % 60)
                return f"{minutes:02d}:{seconds:02d}"

            # 2. Τρέχουσα θέση (Progress)
            current_pos = format_time(pb['progress_ms'])
            
            # 3. Συνολική διάρκεια (Duration)
            total_dur = format_time(track['duration_ms'])
            
            # 4. Ποσοστό % (ως ακέραιος 0-100)
            percent = int((pb['progress_ms'] / track['duration_ms']) * 100)

            # Επιστροφή όλων σε ένα λεξικό για να τα διαλέγεις
            return {
                "info": f"<SPOT_INFO:{name_artist}>",
                "progress": f"<SPOT_POS:{current_pos}>",
                "duration": f"<SPOT_DUR:{total_dur}>",
                "percent": f"<SPOT_PERC:{percent}>"
            }
        
        return None
    except Exception as e:
        print(f"Error fetching Spotify data: {e}")
        return None

# Παράδειγμα ελέγχου (Play/Pause/Next)
def spotify_control(action):
    try:
        sp = get_spotify_client()
        if action == "NEXT": sp.next_track()
        elif action == "PREV": sp.previous_track()
        elif action == "TOGGLE":
            pb = sp.current_playback()
            sp.pause_playback() if pb['is_playing'] else sp.start_playback()
        return True
    except:
        return False

# Test run
if __name__ == "__main__":
    data = get_spotify_detailed_data()
    if data:
        for key, value in data.items():
            print(value)