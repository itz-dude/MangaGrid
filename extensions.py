# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# ------------------------------------------------- #
# ------------------ BEHAVIORS -------------------- #
# ------------------------------------------------- #

def return_flask_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}\\persistent\\db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app

db = SQLAlchemy(return_flask_app())


# ------------------------------------------------- #
# ------------------- SOURCES --------------------- #
# ------------------------------------------------- #

from manga.modules.manganato import Manganato
from manga.modules.mangaschan import Mangaschan
from manga.modules.mangalife import Mangalife
from manga.modules.mangavibe import Mangavibe
from manga.modules.mangahere import Mangahere

sources = {
    'manganato' : {'language': 'en_US', 'object': Manganato},
    'mangaschan' : {'language': 'pt_BR', 'object': Mangaschan},
    # 'mangalife' : {'language': 'en_US', 'object': Mangalife},
    'mangavibe' : {'language': 'pt_BR', 'object': Mangavibe},
    'mangahere' : {'language': 'en_US', 'object': Mangahere},
}