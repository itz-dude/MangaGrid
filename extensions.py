# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import os

from flask import Flask
from flask_cors import CORS
from flask_minify import Minify
from flask_sqlalchemy import SQLAlchemy


# ------------------------------------------------- #
# ------------------ BEHAVIORS -------------------- #
# ------------------------------------------------- #

def return_flask_app():
    app = Flask(__name__)

    app.config['JSON_AS_ASCII'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///persistent/db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.urandom(24)
    Minify(app=app, html=True, js=True, cssless=True)
    CORS(app)

    return app

db = SQLAlchemy(return_flask_app())




# ------------------------------------------------- #
# ------------------- SOURCES --------------------- #
# ------------------------------------------------- #

from manga.modules.manganato import Manganato
from manga.modules.mangaschan import Mangaschan
from manga.modules.kissmanga import Kissmanga
from manga.modules.mangalife import Mangalife
from manga.modules.mangavibe import Mangavibe
from manga.modules.mangahere import Mangahere

sources = {
    'mangaschan' : {'language': 'pt_BR', 'object': Mangaschan},
    'kissmanga' : {'language': 'en_US', 'object': Kissmanga},
    # 'manganato' : {'language': 'en_US', 'object': Manganato},
    # 'mangalife' : {'language': 'en_US', 'object': Mangalife},
    # 'mangavibe' : {'language': 'pt_BR', 'object': Mangavibe},
    # 'mangahere' : {'language': 'en_US', 'object': Mangahere},
}