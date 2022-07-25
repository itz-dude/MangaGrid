# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import os

from flask import Flask, request
from flask_cors import CORS
from flask_minify import Minify
from flask_sqlalchemy import SQLAlchemy


# ------------------------------------------------- #
# ------------------ BEHAVIORS -------------------- #
# ------------------------------------------------- #

# --------------------- APP ----------------------- #
def return_flask_app():
    app = Flask(__name__)

    app.config['JSON_AS_ASCII'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///persistent/db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.urandom(24)
    Minify(app=app, html=True, js=True, cssless=True)
    CORS(app)
    

    return app

# ---------------------- DB ----------------------- #
db = SQLAlchemy(return_flask_app())