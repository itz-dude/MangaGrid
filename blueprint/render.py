# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import json

from flask import Blueprint, redirect, render_template, request

from blueprint.tools import sources
from webscrapping.webscrapping import MangaScrapping


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
render = Blueprint('render', __name__)

@render.route('/')
def index():
    results = {}

    for manga in sources:
        with open(f'webscrapping/results/{manga}_updates.json') as json_file:
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

    if source not in sources and source != 'all':
        return '404 - Page not found', 404
    elif source == 'all':
        output['source'] = sources
    else:
        output['source'] = [source]


    return render_template('search.html', output=output)

@render.route('/manga_viewer')
def manga_viewer():

    # getting url args
    source = request.args.get('source')
    target = request.args.get('target')

    # if source not in sources or not target:
    #     return redirect('/')
    
    return render_template('manga_viewer.html')