# ---------------- DEFAULT IMPORTS ---------------- #
from flask import render_template



# ----------------- STARTING APP ------------------ #


# ------------------ IMPORTING -------------------- #
from extensions import db, return_flask_app

# ----------------- SETTING APP ------------------- #
app = return_flask_app()
db.init_app(app)

# -------------- SETTING BLUEPRINTS --------------- #
from templates.view import render
from manga.view import manga
from users.view import users

app.register_blueprint(render, url_prefix='/')
app.register_blueprint(manga, url_prefix='/api/manga/')
app.register_blueprint(users, url_prefix='/api/users/')

@app.errorhandler(404)
def e404(error):
    return render_template('404.html', output=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)