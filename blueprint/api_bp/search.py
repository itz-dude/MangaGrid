# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures

from flask import Blueprint, jsonify

from webscrapping.webscrapping import MangaScrapping
from blueprint.tools import sources


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
search = Blueprint('search', __name__)

@search.route('/<string:source>/<string:search>')
def index(source, search):
    if source == 'manganato':
        return MangaScrapping().manganato_search(search)
            
    elif source == 'mangalife':
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(MangaScrapping().mangalife_search, search)

            return jsonify(task_1.result())

    elif source == 'mangahere':
        return MangaScrapping().mangahere_search(search)

    else:
        return '', 404