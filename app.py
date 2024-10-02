from flask import Flask, request, jsonify
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

@app.route('/get-playlist', methods=['POST'])
def get_playlist():
    data = request.json
    emotion = data.get('emotion')
    print(f"Received emotion: {emotion}")

    mood_track_seeds = {
        'happy': ['pop', 'dance'],
        'sad': ['acoustic', 'chill'],
        'energetic': ['workout', 'party'],
        'calm': ['ambient', 'sleep']
    }

    genres = mood_track_seeds.get(emotion)
    
    try:
        results = sp.recommendations(seed_genres=genres, limit=10)
        playlists = []

        for track in results['tracks']:
            playlists.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify']
            })

        return jsonify(playlists), 200
    except Exception as e:
        print(e) 
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
