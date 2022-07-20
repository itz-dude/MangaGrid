# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import datetime
import json

from flask import Blueprint, jsonify, session, request
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from tools import c_response

from manga.models import Sources, Mangas, Authors, Genres, Chapters
from users.models import Users, History

# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
users = Blueprint('users', __name__)

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

@users.route('/logout')
def logout():
    session.pop('email', None)
    return jsonify(c_response(200, 'Logged out'))

@users.route('/session/get_profile')
def session_get_profile():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        return jsonify(c_response(200, 'Profile send', user.serialize()))

    else:
        return jsonify(c_response(403, 'Not logged in'))

@users.route('/session/is_alive')
def session_is_alive():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        return jsonify(c_response(200, 'Logged in', {'username': user.username}))

    else:
        return jsonify(c_response(401, 'Not logged in'))

@users.route('/session/update/<section>', methods = ['POST'])
def session_update_info(section):
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        data = request.get_json()

        if not data:
            return jsonify(c_response(401, 'Missing data'))

        if not data.get('target'):
            return jsonify(c_response(401, f'Missing {section}'))

        if section not in ['username', 'password', 'email']:
            return jsonify(c_response(401, 'Invalid section'))

        if user and check_password_hash(user.password, data.get('password')):
            if section == 'username':
                user.username = data.get('target')
                db.session.commit()

                return jsonify(c_response(200, 'Username updated'))
            
            elif section == 'password':
                user.password = generate_password_hash(data.get('target'))
                db.session.commit()

                return jsonify(c_response(200, 'Password updated'))

        else:
            return jsonify(c_response(401, 'Wrong password'))

    else:
        return jsonify(c_response(401, 'Not logged in'))

@users.route('/session/history')
def session_history():
    session['email'] = 'admin@admin.com'
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        
        data = []
        for item in user.history:
            manga = Mangas.query.filter_by(id = item.manga_id).first()
            
            output ={
                'manga_title': manga.title,
                'manga_slug': manga.slug,
                'manga_source': manga.source,
                'image': manga.image,
                'date': item.updated_at
            }
        
            chapter = Chapters.query.filter_by(id = item.chapter_id).first()
            if chapter:
                output['chapter_title'] = chapter.title
                output['chapter_slug'] = chapter.slug
                output['chapter_link'] = chapter.chapter_link
            else:
                output['chapter_title'] = None
                output['chapter_slug'] = None
                output['chapter_link'] = None

            data.append(output)


        data = sorted(data, key=lambda k: k['date'], reverse=True)

        # return jsonify(c_response(200, 'History sent', [item.serialize() for item in user.history.all()]))
        return jsonify(c_response(200, 'History sent', data))

    else:
        return jsonify(c_response(401, 'Not logged in'))