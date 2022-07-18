# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import datetime
import json

from flask import Blueprint, jsonify, session, request
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from users.models import Users
from tools import c_response


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
        email, password = request.args.get('email'), request.args.get('password')
        print(email, password)

        if session.get('login_atp_qt') is None:
            session['login_atp_qt'] = 0
            session['login_atp_ts'] = 0

        ## IMPORTANT: NOT WORKING, NEED TODO
        if session['login_atp_qt'] > 3:
            if session['login_atp_ts'] > datetime.datetime.now() - datetime.timedelta(minutes=5):
                return jsonify(c_response(401, 'Too many login attempts.<br>Please try again in 5 minutes.', {'error': 'too_many_login_attempts'}))

        if not email and not password:
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            return jsonify(c_response(401, 'Missing email or password'))

        user = Users.query.filter_by(email=email).first()

        if not user:
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            return jsonify(c_response(401, 'User not found', {'error': 'email'}))

        if not check_password_hash(user.password, password):
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            return jsonify(c_response(401, 'Wrong password', {'error': 'password'}))

        else:
            session['email'] = email

            return jsonify(c_response(200, 'Logged in'))
            

    elif request.method == 'POST':
        try:
            data = request.get_json()

            if not data:
                return jsonify(c_response(401, 'Missing data'))

            email, password = data.get('email'), data.get('password')

            if not email and not password:
                return jsonify(c_response(401, 'Missing email or password', {'error': 'missing_data'}))

            user = Users.query.filter_by(email=email).first()

            if user:
                return jsonify(c_response(401, 'Email already register', {'error': 'email'}))

            user = Users(email, generate_password_hash(password))

            db.session.add(user)
            db.session.commit()

            return jsonify(c_response(200, 'User created successfully'))
        
        except Exception as e:
            print(e)
            return jsonify(c_response(401, 'Error creating user', {'error': str(e)})), 500