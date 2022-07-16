# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import datetime

from flask import Blueprint, jsonify, session, request
from werkzeug.security import generate_password_hash, check_password_hash

from tools import c_response
from users.models import Users


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
users = Blueprint('users', __name__)

@users.route('/session/is_alive')
def session_is_alive():
    if 'username' in session:
        return jsonify(c_response(200, 'Logged in'))

    else:
        return jsonify(c_response(401, 'Not logged in'))

@users.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        username, password = request.args.get('username'), request.args.get('password')

        if session.get('login_atp_qt') is None:
            session['login_atp_qt'] = 0
            session['login_atp_ts'] = 0

        ## IMPORTANT: NOT WORKING, NEED TODO
        if session['login_atp_qt'] > 3:
            if session['login_atp_ts'] > datetime.datetime.now() - datetime.timedelta(minutes=5):
                return jsonify(c_response(401, 'Too many login attempts.<br>Please try again in 5 minutes.', {'error': 'too_many_login_attempts'}))

        if not username and not password:
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            return jsonify(c_response(401, 'Missing username or password'))

        user = Users.query.filter_by(username=username).first()

        if not user:
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            return jsonify(c_response(401, 'User not found', {'error': 'username'}))

        if not check_password_hash(user.password, password):
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            return jsonify(c_response(401, 'Wrong password', {'error': 'password'}))

        else:
            session['username'] = username

            return jsonify(c_response(200, 'Logged in'))
            

    elif request.method == 'POST':
        return jsonify(c_response(405, 'Not implemented yet'))