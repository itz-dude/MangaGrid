# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures

from flask import Blueprint, jsonify

from webscrapping.webscrapping import MangaScrapping

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
    
    if source == 'manganato':
        manga = MangaScrapping().manganato_access_manga(search)

        if manga is None:
            return jsonify(c_response(404, 'Manga not found')), 404
            
        else: return manga
