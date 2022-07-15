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

    for manga in sources:
        with open(f'manga/results/{manga}_updates.json') as json_file:
            results.update(json.load(json_file))

    index = [key for key in results.keys()]
    index = sorted(index, key=lambda x: results[x]['updated'], reverse=True)

    output = {}

    for key in index:
        output[key] = results[key]

    for index, entrada in enumerate(output):
        if output[entrada]['updated']:
            date = MangaScrapping().get_date_from_string(output[entrada]['updated'])
            output[entrada]['updated'] = MangaScrapping().get_string_from_timestamp(date)


    return render_template('index.html', mangas=output)

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