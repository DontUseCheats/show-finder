from flask import Flask, render_template, redirect, request, requests, session, url_for
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

@app.route("/")
def index():
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

# Spotify sends user back to /callback
@app.route("/callback")
def callback():
    code = request.args.get("code")
    spotify_response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
})
    
    token_data = spotify_response.json()
    access_token = token_data["access_token"]

    session["access_token"] = access_token
    
    return redirect(url_for("artists"))