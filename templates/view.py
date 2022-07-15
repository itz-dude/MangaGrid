# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import json

from flask import Blueprint, redirect, render_template, request, session

from tools import sources
from manga.mangascrapping import MangaScrapping


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
render = Blueprint('render', __name__)

@render.route('/')
def index():
    results = {}

    for manga in sources.keys():
        manga = f'{manga.capitalize()} ({sources[manga]["language"].split("_")[0].upper()})'
        results[manga] = {}
        with open(f'manga/results/{manga.split(" ")[0].lower()}_updates.json') as json_file:
            results[manga].update(json.load(json_file))

        for entrada in results[manga]:
            if results[manga][entrada]['updated']:
                date = MangaScrapping().get_date_from_string(results[manga][entrada]['updated'])
                results[manga][entrada]['updated'] = MangaScrapping().get_string_from_timestamp(date)


    return render_template('index.html', mangas=results)

@render.route('/search')
def search():
    return render_template('search.html')

@render.route('/manga_viewer')
def manga_viewer():
    return render_template('manga_viewer.html')

@render.route('/login')
def login():
    if 'username' in session:
        return redirect('/profile')
    else:
        return render_template('login.html')