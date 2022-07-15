# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures
import threading

from flask import Blueprint, jsonify

from manga.modules.manganato import Manganato
from manga.modules.mangahere import Mangahere
from manga.modules.mangalife import Mangalife

from tools import sources, c_response


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
manga = Blueprint('manga', __name__)

@manga.route('/search/<string:source>/<string:search>')
def search(source, search):
    if source == 'manganato':
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(Manganato().search_title, search)

            return jsonify(task_1.result())
            
    elif source == 'mangalife':
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(Mangalife().search_title, search)

            return jsonify(task_1.result())

    elif source == 'mangahere':
        return Mangahere().search_title(search)

    else:
        return c_response(404, message='Source not found')

@manga.route('/view/<string:source>/<string:search>')
def view(source, search):
    if source not in sources:
        return jsonify(c_response(404, 'Source not found')), 404

    relation = {
        'manganato': Manganato().access_manga,
        'mangahere': Mangahere().access_manga,
    }
    
    try:
        manga = relation[source](search)
    except Exception as e:
        print(f'Error: {e}')
        return jsonify(c_response(500, 'An thread exception, not communicable.')), 500

    if manga is None:
        return jsonify(c_response(404, 'Manga not found')), 404

    else: return manga
