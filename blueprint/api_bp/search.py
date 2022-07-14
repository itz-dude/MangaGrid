# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures

from flask import Blueprint, jsonify

from webscrapping.modules.manganato import Manganato
from webscrapping.modules.mangahere import Mangahere
from webscrapping.modules.mangalife import Mangalife

from blueprint.tools import sources


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
search = Blueprint('search', __name__)

@search.route('/<string:source>/<string:search>')
def index(source, search):
    if source == 'manganato':
        return Manganato().search_title(search)
            
    elif source == 'mangalife':
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(Mangalife().search_title, search)

            return jsonify(task_1.result())

    elif source == 'mangahere':
        return Mangahere().search_title(search)

    else:
        return '', 404