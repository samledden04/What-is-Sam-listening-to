import time, os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__, static_folder='./client/build', static_url_path='')
CORS(app)

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-playback-state user-top-read user-read-recently-played",
    cache_path=".spotify_token_cache"
))

@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:path>")
def serve_react_path(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/current_song')
def current_song():
    try:
        current = sp.current_playback()
        
        if current and current.get('is_playing'):
            track = current['item']
            return jsonify({
                "name" : track['name'],
                "artists" : [artist['name'] for artist in track['artists']],
                "album" : track['album']['name'],
                "image" : track['album']['images'][0]['url'],
                "url" : track['external_urls']['spotify'],
                "id" : track['id']
            })
        else:
            return jsonify({"message" : "Nothing is currently playing."})
    except Exception as e:
        print("Error in /current_song:", e)
        return jsonify({"message" : "Error retrieving song."}), 500

@app.route('/top_tracks')
def top_tracks():
    try:
        tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
        return jsonify( [{
                'id' : t['id'],
                'name' : t['name'],
                'artists' : [artist['name'] for artist in t['artists']],
                'image' : t['album']['images'][0]['url'],
                'url' : t['external_urls']['spotify'],
            } for t in tracks['items']]
        )
    except Exception as e:
        print("Error in /top_tracks:", e)
        return jsonify({"message" : "Error retrieving top tracks."}), 500

@app.route('/recently_played')
def recently_played():
    try:
        tracks = sp.current_user_recently_played(limit=10)
        # print(tracks)
        return jsonify( 
            [{
                'id' : t['track']['id'],
                'name' : t['track']['name'],
                'artists' : [artist['name'] for artist in t['track']['artists']],
                'image' : t['track']['album']['images'][0]['url'],
                'url' : t['track']['external_urls']['spotify'],
                'played_at' : t['played_at']
            } for t in tracks['items']]
        )
    except Exception as e:
        print("Error in /recently_played:", e)
        return jsonify({"message" : "Error retrieving recently played songs."}), 500

@app.route('/top_artists')
def top_artists():
    try:
        artists = sp.current_user_top_artists(limit=10, time_range="short_term")
        return jsonify([{
                'id' : artist['id'],
                'name' : artist['name'],
                'image' : artist['images'][0]['url'],
                'url' : artist['external_urls']['spotify'],
            } for artist in artists['items']]
        )
    except Exception as e:
        print("Error in /top_artists", e)
        return jsonify({"message" : "Error retrieving top artists."}), 500
    

# @app.route('/')
# def home():
#     return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)