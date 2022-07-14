# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import os

from flask_minify import Minify

# ------------------------------------------------- #
# ----------------- STARTING APP ------------------ #
# ------------------------------------------------- #


# ------------------ IMPORTING -------------------- #
from extensions import db, return_flask_app

# ----------------- SETTING APP ------------------- #
app = return_flask_app()
db.init_app(app)

app.config['JSON_AS_ASCII'] = False
app.secret_key = os.urandom(24)

Minify(app=app, html=True, js=True, cssless=True)

# -------------- SETTING BLUEPRINTS --------------- #
from blueprint.render import render
from blueprint.api import api

app.register_blueprint(render, url_prefix='/')
app.register_blueprint(api, url_prefix='/api/')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)