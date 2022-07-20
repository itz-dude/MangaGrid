# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import json

from flask import Blueprint, redirect, render_template, request, session

from extensions import sources
from tools import pprint
from manga.mangascrapping import MangaScrapping


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
render = Blueprint('render', __name__)

@render.route('/')
def index():
    results = {}
    error = False

    for manga in sources.keys():
        try:
            manga = f'{manga.capitalize()} ({sources[manga]["language"].split("_")[0].upper()})'
            results[manga] = {}
            with open(f'manga/results/{manga.split(" ")[0].lower()}_updates.json') as json_file:
                results[manga].update(json.load(json_file))

            for entrada in results[manga]:
                if results[manga][entrada]['updated']:
                    date = MangaScrapping().get_date_from_string(results[manga][entrada]['updated'])
                    results[manga][entrada]['updated'] = MangaScrapping().get_string_from_timestamp(date)
        
        except FileNotFoundError:
            error = True
            pprint(f'[!] ERROR: / - Archive not found for {manga}', 'red')

    if error:
        pprint(f'[!] ALERT: / - Have you run the "manga/auto_update.py"?', 'yellow')

    return render_template('index.html', mangas=results)

@render.route('/search')
def search():
    return render_template('search.html')

@render.route('/manga_viewer')
def manga_viewer():
    return render_template('manga_viewer.html')

@render.route('/chapter_viewer')
def chapter_viewer():
    return render_template('chapter_viewer.html')

@render.route('/register')
@render.route('/login')
def login():
    if 'username' in session:
        return redirect('/profile')
        
    else:
        output='login'
        if request.path == '/register':
            output='register'
        return render_template('login.html', output=output)

@render.route('/profile')
@render.route('/profile/history')
def profile():
    if 'email' not in session:
        return redirect('/login')
        
    else:
        output = 'profile'
        if request.path == '/profile/history':
            output = 'history'
        return render_template('profile.html', output=output)