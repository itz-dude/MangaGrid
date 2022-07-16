# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import os


# ------------------------------------------------- #
# ----------------- STARTING APP ------------------ #
# ------------------------------------------------- #


# ------------------ IMPORTING -------------------- #
from extensions import db, return_flask_app

# ----------------- SETTING APP ------------------- #
app = return_flask_app()
# db.init_app(app)


# -------------- SETTING BLUEPRINTS --------------- #
from templates.view import render
from manga.view import manga
from users.view import users

app.register_blueprint(render, url_prefix='/')
app.register_blueprint(manga, url_prefix='/api/manga/')
app.register_blueprint(users, url_prefix='/api/users/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)