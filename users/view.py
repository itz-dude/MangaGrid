# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

from flask import Blueprint, jsonify, session, request

from tools import c_response


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
users = Blueprint('users', __name__)

@users.route('/login', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'username' in session:
            return jsonify(c_response(200, 'Logged in'))

        else:
            return jsonify(c_response(401, 'Not logged in'))

    elif request.method == 'POST':
        return jsonify(c_response(400, 'Not implemented yet'))