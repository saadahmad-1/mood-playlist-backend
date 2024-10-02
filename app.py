from flask import Flask, request, jsonify
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

def detect_emotion_vader(text):
    scores = sid.polarity_scores(text)
    compound_score = scores['compound']

    if compound_score >= 0.5:
        return 'happy'
    elif 0 < compound_score < 0.5:
        return 'calm'
    elif -0.5 <= compound_score <= 0:
        return 'sad'
    else:
        return 'energetic'

@app.route('/get-playlist', methods=['POST'])
@app.route('/get-playlist', methods=['POST'])
def get_playlist():
    try:
        data = request.json

        emotionText = data.get('emotionText')
        if not emotionText:
            return jsonify({"error": "No 'emotionText' provided or it is empty"}), 400

        logging.info(f"Received emotionText: {emotionText}")

        emotion = detect_emotion_vader(emotionText)
        logging.info(f"Detected emotion: {emotion}")

        mood_track_seeds = {
            'happy': ['pop', 'dance'],
            'sad': ['acoustic', 'chill'],
            'energetic': ['workout', 'party'],
            'calm': ['ambient', 'sleep']
        }

        genres = mood_track_seeds.get(emotion)
        if not genres:
            return jsonify({"error": f"No genres found for emotion '{emotion}'"}), 400

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
        logging.error(f"Error occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
