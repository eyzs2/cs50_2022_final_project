from crypt import methods
import os
import spotipy
import uuid

# Spotipy library must be installed for the successful functioning of the application (pip3 install spotipy)

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
from functools import wraps
from statistics import stdev, mean


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
CLI_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLI_SEC = os.environ.get("SPOTIPY_CLIENT_SECRET")
SCOPE = "user-library-read, user-top-read, playlist-modify-private"
Session(app)

caches_folder = "./.spotify_caches/"
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

# Cache folder on device, adapted from Spotipy example
def session_cache_path():
    return caches_folder + session.get('uuid')

# Handing authentication and cache management
def auth_manager():
    cache_handler = CacheFileHandler(cache_path=session_cache_path())
    auth_manager = SpotifyOAuth(scope=SCOPE, cache_handler=cache_handler, show_dialog=True)
    return auth_manager, cache_handler

def login_required(f):
    # Adapted from CS50 Finance, used to verify authorisation of Spotify access
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('uuid'):
            # Sets session id if not present
            session['uuid'] = str(uuid.uuid4())
        auth_tuple = auth_manager()
        if not auth_tuple[0].validate_token(auth_tuple[1].get_cached_token()):
            # If not logged in to Spotify account
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    auth_tuple = auth_manager()
    sp = spotipy.Spotify(auth_manager=auth_tuple[0])
    name = sp.me()["display_name"]
    return render_template("index.html", name=name)

# Redirects to link to authorise access
@app.route("/login")
def login():
    auth_tuple = auth_manager()
    auth_url = auth_tuple[0].get_authorize_url()
    return render_template("indexed.html", auth_url=auth_url)

# Redirects from Spotify authorisation
@app.route("/callback")
def callback():
    if request.args.get("code"):
        auth_tuple = auth_manager()
        auth_tuple[0].get_access_token(request.args.get("code"))
        session["logged_in"] = True
        flash("Login successful!")
    return redirect("/")

@app.route("/logout")
def logout():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session["logged_in"] = False
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect("/")

@app.route("/musicpast")
@login_required
def musicpast():
    # Analyse songs/artists that have been listened to many times in past (i.e. since account creation to month before present)
    auth_tuple = auth_manager()
    sp = spotipy.Spotify(auth_manager=auth_tuple[0])
    # Obtains list of top user tracks using built-in Spotify function
    track = sp.current_user_top_tracks(time_range="long_term")
    toptracks = track["items"]
    acns = []
    dnce = []
    dncetrack = []
    value = 0
    enrg = []
    asum, dsum, esum = "It seems, in terms of instrumentals, you're more ","On average, it seems your music history tends towards the ",""
    for item in toptracks:
        # Appends acousticness, danceability and energy of each top track to list
        track_analysis = sp.audio_features(tracks=item["id"])[0]
        acns.append(track_analysis["acousticness"])
        dnce.append(track_analysis["danceability"])
        enrg.append(track_analysis["energy"])
    # Calculate standard deviation, mean of certain audio features
    enrgsd = stdev(enrg)
    acnsavg = mean(acns)
    dnceavg = mean(dnce)
    # Present statements to user based on calculations
    if acnsavg > 0.5:
        asum = asum + "adventurous..."
    elif acnsavg <= 0.5:
        asum = asum + "of a purist..."
    if enrgsd > 0.35:
        esum = "From what I can see, the energy of your music has varied over your musical journey..."
    elif enrgsd <= 0.35:
        esum = "Your musical energy seems consistent and steady, perhaps you find comfort in a certain familiarity?"
    if dnceavg > 0.5:
        dsum = dsum + "danceable side..."
        value = max(dnce)
    elif dnceavg <= 0.5:
        dsum = dsum + "undanceable side..."
        value = min(dnce)
    index = dnce.index(value)
    dncetrack = toptracks[index]

    return render_template("musicpast.html", asum=asum, esum=esum, dsum=dsum, dncetrack=dncetrack)

@app.route("/musicfuture", methods=["GET", "POST"])
@login_required
def musicfuture():
    auth_tuple = auth_manager()
    sp = spotipy.Spotify(auth_manager=auth_tuple[0])
    if request.method == "POST":
        # Creates playlist and adds tracks to said playlist
        futuretracks = list(eval(request.form.get("futuretracks")))
        user_id = sp.me()['id']
        new_playlist = sp.user_playlist_create(user=user_id,name="Your Music Future Playlist", public=False, description="Playlist containing recommendations from the SpotiPsychic based on your listening history.")
        playlist_id = new_playlist["id"]
        recommendedtracks = []
        for item in futuretracks:
            recommendedtracks.append(item["id"])
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=recommendedtracks)
        flash("Playlist successfully added!")
        return render_template("musicfutureadded.html", futuretracks=futuretracks)

    else:
        # Obtains limited number of top artists/tracks in short-term
        artists = sp.current_user_top_artists(limit=2, time_range="short_term")
        tracks = sp.current_user_top_tracks(limit=3, time_range="short_term")
        seed_artists = []
        seed_tracks = []
        for item in artists["items"]:
            seed_artists.append(item["id"])
        for item in tracks["items"]:
            seed_tracks.append(item["id"])
        # Get recommendations using Spotify's built-in recommendations function
        future = sp.recommendations(seed_artists=seed_artists, seed_tracks=seed_tracks, limit=25)
        futuretracks = future["tracks"]
        return render_template("musicfuture.html", futuretracks=futuretracks, artists=artists["items"], tracks=tracks["items"])