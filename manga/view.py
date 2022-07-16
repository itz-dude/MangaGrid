# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures
import threading

from flask import Blueprint, jsonify

from extensions import sources
from tools import c_response

# ------------------------------------------------- #
# -------------------- TOOLS ---------------------- #
# ------------------------------------------------- #

def process_generator(func, args):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        task_1 = executor.submit(func, args)
        return task_1.result()

# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
manga = Blueprint('manga', __name__)

@manga.route('/avaliable_sources')
def avaliable_sources():
    data = {}
    for s in sources:
        data[s] = sources[s]['language']

    return jsonify(c_response(200, 'Sources avaliable', data))

@manga.route('/search/<string:source>/<string:search>')
def search(source, search):
    try:
        obj = sources[source]['object']
        task = process_generator(obj().search_title, search)

        if task:
            return jsonify(c_response(200, 'Search results', task))

        else:
            return jsonify(c_response(404, 'Search results'))

    except KeyError:
        return jsonify(c_response(400, 'Source not avaliable'))

    except Exception as e:
        print(f'LOG: ERROR - Search - {source} - {search}')
        return jsonify(c_response(500, str(e)))

@manga.route('/view/<string:source>/<string:search>')
def view(source, search):
    try:
        manga = process_generator(sources[source]['object']().access_manga, search)

        if manga is None:
            return jsonify(c_response(404, 'Manga not found')), 404

        else: return jsonify(c_response(200, 'Target captured', manga))

    except KeyError:
        return jsonify(c_response(404, 'Source not found')), 404

    except Exception as e:
        print(f'Error: {e}')
        return jsonify(c_response(500, 'An thread exception, not communicable.')), 500