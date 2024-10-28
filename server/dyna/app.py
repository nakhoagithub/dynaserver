import os
from flask import Flask
from flask_cors import CORS
from config import Config


class Server(Flask):
    pass

# app
app = Server(__name__, static_folder="static/")

# config
app.config.from_object(Config())

CORS(
    app, 
    resources={
        r"/api/*": {
            "origins": os.environ.get("CORS_ALLOW_ORIGINS", "*")
        }
    },
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-App-Code"],
    methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"]
)