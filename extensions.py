import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def return_flask_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}\\persistent\\db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app

db = SQLAlchemy(return_flask_app())