from flask import Flask, render_template, redirect, request, session, url_for, jsonify
import requests
import os
from dotenv import load_dotenv

# loads the actual .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# declare variables set to saved variables in prviate .env file
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

# helper function for refresh token
def refresh_access_token():
    refresh_token = session.get("refresh_token")
    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })
    new_token = response.json()["access_token"]
    session["access_token"] = new_token
    return new_token

@app.route("/")
def index():
    # checks oAuth and if not truthy then route to homepage
    if session.get("access_token"):
        return redirect(url_for("artists"))
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

# User is directed to Spotify
@app.route("/auth/spotify")
def auth_spotify():
    scope = "user-top-read"
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(auth_url)

# oAuth setup
# Spotify sends user back to /callback and checks oAuth
@app.route("/callback")
def callback():
    code = request.args.get("code")
    # post request to spotify to authorize request
    spotify_response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
})
    
    token_data = spotify_response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")

    session["access_token"] = access_token
    session["refresh_token"] = refresh_token
    
    return redirect(url_for("artists"))

# redirect to artists page
@app.route("/artists")
def artists():
    # checks oAuth
    token = session.get("access_token")
    if not token:
        return redirect(url_for("login"))
    
    # call Spotify API for top artists
    response = requests.get("https://api.spotify.com/v1/me/top/artists", headers={
        "Authorization": f"Bearer {token}"
    })

    if response.status_code == 401:
        token = refresh_access_token()
        response = requests.get("https://api.spotify.com/v1/me/top/artists", headers={
            "Authorization": f"Bearer {token}"
        })

    data = response.json()
    top_artists = data.get("items", [])

    return render_template("artists.html", artists=top_artists)


@app.route("/artist/<path:artist_name>")
def artist_concerts(artist_name):
    token = session.get("access_token")
    if not token:
        return redirect(url_for("login"))
    
    # get ticket button takes to Ticketmaster page
    response = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json", params={
            "apikey": TICKETMASTER_API_KEY,
            "keyword": artist_name,
            "classificationName": "music",
            "countryCode": "US",
            "size": 20
        }
    )

    data = response.json()
    events = data.get("_embedded", {}).get("events", [])

    return render_template("artists.html", events=events)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))