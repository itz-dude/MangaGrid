# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
from concurrent.futures import thread
import os
import threading

from webscrapping.webscrapping import MangaScrapping


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

# -------------- SETTING BLUEPRINTS --------------- #
from blueprint.render import render
from blueprint.api import api

app.register_blueprint(render, url_prefix='/')
app.register_blueprint(api, url_prefix='/api/')



if __name__ == '__main__':
    # try:
    #     threading.Thread(target=MangaScrapping().routine_initialization).start()
    # except Exception as e:
    #     print(f'Error: {e}')

    app.run(host='0.0.0.0', debug=True)