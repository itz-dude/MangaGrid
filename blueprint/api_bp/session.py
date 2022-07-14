# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

from flask import Blueprint, jsonify, session, request

from blueprint.tools import c_response


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
session_bp = Blueprint('session', __name__)

@session_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'username' in session:
            return jsonify(c_response(200, 'Logged in'))

        else:
            return jsonify(c_response(401, 'Not logged in'))

    elif request.method == 'POST':
        return jsonify(c_response(400, 'Not implemented yet'))