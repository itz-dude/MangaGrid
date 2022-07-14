# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures

from flask import Blueprint, jsonify

from webscrapping.modules.manganato import Manganato
from webscrapping.modules.mangahere import Mangahere

from blueprint.api_bp.search import search
from blueprint.tools import sources, c_response


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
api = Blueprint('api', __name__)
api.register_blueprint(search, url_prefix='/search/')

@api.route('/manga/<string:source>/<string:search>')
def manga(source, search):
    if source not in sources:
        return {'error': 'Source not found', 'status': 404}, 404

    relation = {
        'manganato': Manganato().access_manga,
        'mangahere': Mangahere().access_manga,
    }
    
    manga = relation[source](search)

    if manga is None:
        return jsonify(c_response(404, 'Manga not found')), 404

    else: return manga
