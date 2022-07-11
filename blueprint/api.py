# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures
import json

from flask import Blueprint, jsonify

from webscrapping.webscrapping import MangaScrapping


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
api = Blueprint('api', __name__)

@api.route('/search/<string:source>/<string:search>')
def index(source, search):

    print(source, search)

    if source == 'manganato':
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(MangaScrapping().manganato_search, search)

            return jsonify(task_1.result())
            
    elif source == 'mangalife':
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(MangaScrapping().mangalife_search, search)

            return jsonify(task_1.result())

    else:
        return '', 404