from flask import Flask, render_template, redirect, request, session, url_for
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

CLIENT_ID = os.getenv("CLIENT_SECRET_KEY")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URL = os.getenv("SPOTIFY_REDIRECT_URL")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/auth/spotify")
def auth_spotify():
    scope = "user-top-read"
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URL}"
        f"&scope={scope}"
    )
    return redirect(auth_url)