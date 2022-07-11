# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import json

from flask import Blueprint, render_template

from webscrapping.webscrapping import MangaScrapping


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
render = Blueprint('render', __name__)

@render.route('/')
def index():
    results = {}

    with open('webscrapping/results/manganato_updates.json') as json_file:
        results.update(json.load(json_file))

    with open('webscrapping/results/mangalife_updates.json') as json_file:
        results.update(json.load(json_file))

    index = [key for key in results.keys()]
    index = sorted(index, key=lambda x: results[x]['updated'], reverse=True)

    output = {}

    for key in index:
        output[key] = results[key]

    for index, entrada in enumerate(output):
        date = MangaScrapping().get_date_from_string(output[entrada]['updated'])
        output[entrada]['updated'] = MangaScrapping().get_string_from_timestamp(date)


    return render_template('index.html', mangas=output)

@render.route('/search/<string:source>/<string:search>')
def search(source, search):
    output = {}
    output['target'] = search

    sources = [
        'manganato',
        'mangalife'
    ]

    if source not in sources and source != 'all':
        return '404 - Page not found', 404
    elif source == 'all':
        output['source'] = sources
    else:
        output['source'] = source


    return render_template('search.html', output=output)