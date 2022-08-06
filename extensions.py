# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import datetime
import os

from flask import Flask
from flask_cors import CORS
from flask_minify import Minify
from flask_sqlalchemy import SQLAlchemy


# ------------------------------------------------- #
# ------------------ BEHAVIORS -------------------- #
# ------------------------------------------------- #

# --------------------- APP ----------------------- #
def return_flask_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///persistent/db.sqlite3'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://grigio888:kiju1475@grigio888.mysql.pythonanywhere-services.com/grigio888$app_production'
    # app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size' : 100, 'pool_recycle' : 280, 'pool_pre_ping' : True}
    app.config['JSON_AS_ASCII'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] =  datetime.timedelta(days=1)
    app.secret_key = os.urandom(24)
    Minify(app=app, html=True, js=True, cssless=True)
    CORS(app)


    return app

# ---------------------- DB ----------------------- #
db = SQLAlchemy(return_flask_app())