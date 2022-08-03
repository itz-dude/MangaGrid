# ---------------- DEFAULT IMPORTS ---------------- #

import datetime

from flask import Blueprint, jsonify, session, request
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from tools.tools import c_response, pprint, check_email

from manga.models import Sources, Mangas, Chapters
from users.models import Ratings, Users, History, Favorites, LoginAttempts





# ---------------- STARTING ROUTE ----------------- #

users = Blueprint('users', __name__)






# --------------------- LOGIN ---------------------- #

@users.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        email, password, remember = request.args.get('email'), request.args.get('password'), request.args.get('remember')

        if not check_email(email):
            return jsonify(c_response(400, 'Invalid email'))

        user = Users.query.filter_by(email=email).first()

        if not user:
            return jsonify(c_response(400, 'User not found'))

        elif not check_password_hash(user.password, password):
            attempt = LoginAttempts.query.filter_by(user_email=email).first()

            if not attempt:
                attempt = LoginAttempts(user_email=email, attempts=1, last_attempt=datetime.datetime.now())
                db.session.add(attempt)
                db.session.commit()

            elif attempt.last_attempt < datetime.datetime.now() - datetime.timedelta(minutes=5):
                attempt.attempts = 1
                attempt.last_attempt = datetime.datetime.now()
                db.session.commit()

            elif attempt.attempts < 3:
                attempt.attempts += 1
                attempt.last_attempt = datetime.datetime.now()
                db.session.commit()

            else:
                attempt = LoginAttempts.query.filter_by(user_email=email).first()
                attempt.last_attempt = datetime.datetime.now()

                pprint(f'[i] Info: {request.path} - {email} blocked from login by 24hrs.', 'yellow')
                return jsonify(c_response(400, 'Too many attempts. User blocked for 24hrs.'))

            pprint(f'[i] Info: {request.path} - Wrong password for {email}.', 'yellow')
            return jsonify(c_response(401, 'Wrong password', {'error': 'password'}))

        else:
            session['email'] = email
            session['theme'] = user.theme

            if remember == 'true':
                session.permanent = True

            pprint(f'[i] Info: {request.path} - User {email} logged in.', 'green')
            return jsonify(c_response(200, 'Logged in'))


    elif request.method == 'POST':
        try:
            data = request.get_json()

            if not data:
                pprint(f'[i] Info: {request.path} - Missing information on requisition.', 'yellow')
                return jsonify(c_response(401, 'Missing data'))

            email, password = data.get('email'), data.get('password')

            if not email and not password:
                pprint(f'[i] Info: {request.path} - Missing information on requisition.', 'yellow')
                return jsonify(c_response(401, 'Missing email or password', {'error': 'missing_data'}))

            if not check_email(email):
                return jsonify(c_response(400, 'Invalid email'))

            if not password:
                pprint(f'[i] Info: {request.path} - Missing password.', 'yellow')
                return jsonify(c_response(401, 'Missing password'))

            user = Users.query.filter_by(email=email).first()

            if user:
                pprint(f'[i] Info: {request.path} - User {email} already exists.', 'yellow')
                return jsonify(c_response(401, 'Email already register', {'error': 'email'}))

            user = Users(email, generate_password_hash(password))

            db.session.add(user)
            db.session.commit()

            return jsonify(c_response(200, 'User created successfully'))

        except Exception as e:
            print(e)
            return jsonify(c_response(401, 'Error creating user', {'error': str(e)})), 500



# -------------------- LOGOUT ---------------------- #

@users.route('/logout')
def logout():
    pprint(f'[i] Info: {request.path} - User {session.get("email")} logged out.', 'green')
    session.pop('email', None)

    return jsonify(c_response(200, 'Logged out'))



# -------------------- SESSION --------------------- #

# -------------------- PROFILE --------------------- #
@users.route('/session/is_alive')
def session_is_alive():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()

        pprint(f'[i] Info: {request.path} - User {user.email} is logged.', 'green')
        return jsonify(c_response(200, 'Logged in', {'username': user.username, 'theme': user.theme}))

    else:
        session['theme'] = session.get('theme', 'light')
        session['cookies_acpted'] = session.get('cookies_acpted', False)
        return jsonify(c_response(401, 'Not logged in', {'theme': session['theme'], 'cookies_acpted': session['cookies_acpted']}))

@users.route('/session/cookies_accepted', methods=['POST'])
def session_cookies_accepted():
    session['cookies_acpted'] = True
    return jsonify(c_response(200, 'Cookies accepted'))


@users.route('/session/get_profile')
def session_get_profile():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()

        pprint(f'[i] Info: {request.path} - User {user.email} requested profile.', 'green')
        return jsonify(c_response(200, 'Profile send', user.serialize()))

    else:
        return jsonify(c_response(403, 'Not logged in'))


@users.route('/session/update/<section>', methods = ['POST'])
def session_update_info(section):
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        data = request.get_json()

        if not data:
            pprint(f'[i] Info: {request.path} - Missing information on requisition.', 'yellow')
            return jsonify(c_response(401, 'Missing data'))

        if not data.get('target'):
            pprint(f'[i] Info: {request.path} - Missing target on requisition.', 'yellow')
            return jsonify(c_response(401, f'Missing {section}'))

        if section not in ['main_section', 'username', 'password', 'email']:
            pprint(f'[i] Info: {request.path} - Invalid section on requisition.', 'yellow')
            return jsonify(c_response(401, 'Invalid section'))

        if section == 'main_section':
            user.main_page = data.get('target', '/')
            db.session.commit()

            pprint(f'[i] Info: {request.path} - User {user.username} updated main section.', 'green')
            return jsonify(c_response(200, 'Main section updated'))

        elif user and check_password_hash(user.password, data.get('password')):
            if section == 'username':
                pprint(f'[i] Info: {request.path} - User {user.username} updated username.', 'green')
                user.username = data.get('target')
                db.session.commit()

                return jsonify(c_response(200, 'Username updated'))

            elif section == 'password':
                user.password = generate_password_hash(data.get('target'))
                db.session.commit()

                pprint(f'[i] Info: {request.path} - User {user.username} updated password.', 'green')
                return jsonify(c_response(200, 'Password updated'))

        else:
            pprint(f'[i] {request.path} - Wrong password for {user.username}.', 'red')
            return jsonify(c_response(401, 'Wrong password'))

    else:
        return jsonify(c_response(401, 'Not logged in'))


@users.route('/session/theme', methods = ['GET', 'POST'])
def session_theme():
    if request.method == 'GET':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()

            pprint(f'[i] Info: {request.path} - User {user.email} requested theme.', 'green')
            return jsonify(c_response(200, 'Theme send', {'theme': user.theme}))

        else:
            return jsonify(c_response(200, 'Theme send', {'theme': session.get('theme', 'light')}))

    elif request.method == 'POST':
        if session.get('theme'):
            theme = session.get('theme', 'light')

            if theme == 'light': session['theme'] = 'dark'
            else: session['theme'] = 'light'

            if 'email' in session:
                user = Users.query.filter_by(email=session['email']).first()
                user.theme = session['theme']
                db.session.commit()

            return jsonify(c_response(200, 'Theme updated'))

        else:

            if session.get('theme') == 'dark':
                session['theme'] = 'light'
                return jsonify(c_response(200, 'Theme updated'))

            else:
                session['theme'] = 'dark'
                return jsonify(c_response(200, 'Theme updated'))


# -------------------- HISTORY --------------------- #
@users.route('/session/history')
def session_history():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        data = []
        for item in History.query.filter_by(user_id=user.id).order_by(History.updated_at.desc()).all():
            manga = Mangas.query.filter_by(id = item.manga_id).first()
            source = Sources.query.filter_by(id = manga.source).first()
            history = History.query.filter_by(user_id=user.id, manga_id=manga.id).first()

            if len(history.chapters.all()) > 0:
                output = manga.serialize() | history.serialize() | {'manga_source': source.slug}
                output = output | history.chapters.order_by(Chapters.id.desc()).first().serialize() if history.chapters.count() > 0 else output
                data.append(output)

        data = sorted(data, key=lambda k: k['history_updated_at'], reverse=True)

        pprint(f'[i] Info: {request.path} - User {user.username} requested history.', 'green')
        return jsonify(c_response(200, 'History sent', data))

    else:
        return jsonify(c_response(401, 'Not logged in'))


@users.route('/session/history/<string:param>/<manga_slug>')
def session_history_manga(param, manga_slug):
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        try:
            filter = []

            if param == 'latest':
                filter.append(History.updated_at.desc())

            manga = Mangas.query.filter_by(slug = manga_slug).first()
            history = user.history.filter_by(manga_id = manga.id).order_by(*filter).first()

            data = {}
            if history and len(history.chapters.all()) > 0:
                data = history.serialize() | manga.serialize()
                data = data | history.chapters.order_by(Chapters.id.desc()).first().serialize() if history.chapters.count() > 0 else {}

                return jsonify(c_response(200, 'History sent', data))

            else:
                raise Exception()

        except:
            return jsonify(c_response(401, 'History not found'))

    else:
        return jsonify(c_response(401, 'Not logged in'))

@users.route('/session/history/reset', methods = ['POST'])
@users.route('/session/history/reset/<string:manga_slug>', methods = ['POST'])
def session_history_reset(manga_slug = None):
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()

        try:
            filter = [History.user_id == user.id,]
            manga = Mangas.query.filter_by(slug = manga_slug).first()
            if manga:
                filter.append(History.manga_id == manga.id)

            history = History.query.filter(*filter).all()
            for item in history:
                item.chapters = []
                db.session.commit()
                db.session.delete(item)
                db.session.commit()

            pprint(f'[i] Info: {request.path} - User {user.username} reset history.', 'green')
            return jsonify(c_response(200, 'History reset'))

        except Exception as e:
            print(e)
            return jsonify(c_response(401, 'History not found'))

    else:
        return jsonify(c_response(401, 'Not logged in'))

@users.route('/session/history/set/<string:option>/<string:manga>', methods = ['POST'])
def session_history_set(option = None, manga = None):
    if not option or not manga:
        return jsonify(c_response(401, 'Invalid parameters'))
    elif not 'email' in session:
        return jsonify(c_response(401, 'Not logged in'))


    user = Users.query.filter_by(email=session['email']).first()
    manga = Mangas.query.filter_by(slug = manga).first()
    if not manga:
        return jsonify(c_response(401, 'Manga not found'))

    history = History.query.filter_by(user_id = user.id, manga_id = manga.id).first()
    if not history:
        history = History(user_id = user.id, manga_id = manga.id)
        db.session.add(history)
        db.session.commit()


    if option == 'read_all':
        history.chapters = [chapter for chapter in manga.chapters]
        history.updated_at = datetime.datetime.now()
        db.session.commit()
        return jsonify(c_response(200, 'History updated'))

    elif option == 'unread_all':
        history.chapters = []
        history.updated_at = datetime.datetime.now()
        db.session.commit()
        return jsonify(c_response(200, 'History updated'))

    else:
        return jsonify(c_response(401, 'Invalid parameters'))


# -------------------- FAVORITES --------------------- #
@users.route('/session/favorite/filter/<filter>')
def session_favorites(filter = 'manga_title'):
    if request.method == 'GET':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()

            data = []
            for fav in user.favorites:
                manga = Mangas.query.filter_by(id = fav.manga_id).first()
                source = Sources.query.filter_by(id = manga.source).first()
                history = user.history.filter_by(manga_id = fav.manga_id).first()


                output = manga.serialize() | fav.serialize()
                output = output | history.serialize() if history else {}
                output = output | history.chapters.order_by(Chapters.id.desc()).first().serialize() if history.chapters.count() > 0 else output
                output = output | {'manga_source': source.slug}

                if len(output['manga_title']) > 40:
                    output['manga_title'] = output['manga_title'][:40] + '...'

                if history and history.chapters:
                    if history.chapters.count() == 0:
                        output['read_status'] = 'Unreaded.'
                    elif manga.chapters.order_by(Chapters.id.desc()).first().created_at > history.updated_at:
                        output['read_status'] = 'New Chapters!'
                    elif manga.chapters.count() > history.chapters.count():
                        output['read_status'] = f'{manga.chapters.count() - history.chapters.count()} unread chapters!'
                    # else:
                    #     output['read_status'] = 'All chapters readed.'

                data.append(output)

            if filter == 'favorites_created_at':
                data = sorted(data, key=lambda k: k[filter], reverse=True)
            else:
                data = sorted(data, key=lambda k: k[filter])

            pprint(f'[i] Info: {request.path} - Favorites of {user.username}', 'green')
            return jsonify(c_response(200, 'Favorites sent', data))

        else:
            return jsonify(c_response(401, 'Not logged in'))

@users.route('/session/favorite/<string:manga>', methods = ['GET', 'POST'])
def session_favorites_manga(manga = None):
    if request.method == 'GET':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            manga = Mangas.query.filter_by(slug = manga).first()

            if user.favorites.filter_by(manga_id = manga.id).first():
                pprint(f'[i] Info: {request.path} - {user.username} requested in his favorites and have.', 'green')
                return jsonify(c_response(200, 'Sended', {'status': 'true'}))

            else:
                pprint(f'[i] Info: {request.path} - {user.username} requested in his favorites and have not.', 'green')
                return jsonify(c_response(200, 'Sended', {'status': 'false'}))

        else:
            return jsonify(c_response(401, 'Not logged in'))

    elif request.method == 'POST':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()

            manga = Mangas.query.filter_by(slug = manga).first()
            if not manga:
                pprint(f'[i] Info: {request.path} - Manga {manga} not found.', 'yellow')
                return jsonify(c_response(401, 'Manga not found'))

            removed = False
            for item in user.favorites:
                if item.manga_id == manga.id:
                    favorite = Favorites.query.filter_by(user_id = user.id, manga_id = manga.id).first()
                    user.favorites.remove(favorite)
                    db.session.delete(favorite)
                    db.session.commit()
                    removed = True

                    pprint(f'[i] Info: {request.path} - Removed manga {manga} from {user.username} favorites.', 'green')
                    return jsonify(c_response(200, 'Manga already in favorites. Removed', {'operation': 'removed'}))

            if not removed:
                favorite = Favorites(user_id = user.id, manga_id = manga.id)
                db.session.add(favorite)
                db.session.commit()
                user.favorites.append(favorite)
                db.session.commit()
                pprint(f'[i] Info: {request.path} - Added manga {manga} to {user.username} favorites.', 'green')
                return jsonify(c_response(200, 'Manga added to favorites', {'operation': 'added'}))

        else:
            return jsonify(c_response(401, 'Not logged in'))


# -------------------- RATING --------------------- #
@users.route('/session/rating/<string:manga>')
@users.route('/session/rating/<string:manga>/<int:rating_i>', methods = ['POST'])
def session_rating(manga, rating_i = None):
    if request.method == 'GET':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            manga = Mangas.query.filter_by(slug=manga).first()
            rating = user.ratings.filter_by(user_id=user.id, manga_id=manga.id).first()

            if rating:
                pprint(f'[i] Info: {request.path} - Rating of {manga.title} from {user.username}', 'green')
                return jsonify(c_response(200, 'Rating sent', rating.rating))

            else:
                try:
                    pprint(f'[i] Info: {request.path} - User {user.username} havent rated {manga.title} yet.', 'green')
                    return jsonify(c_response(200, 'Not rated', None))
                except:
                    return jsonify(c_response(200, 'Rating not found'))

        else:
            return jsonify(c_response(401, 'Not logged in'))

    elif request.method == 'POST':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            manga = Mangas.query.filter_by(slug=manga).first()

            rating = Ratings.query.filter_by(user_id=user.id, manga_id=manga.id).first()
            if rating:
                rating.rating = rating_i
                db.session.commit()

                pprint(f'[i] Info: {request.path} - User {user.username} rated {manga.title} with {rating_i} star.', 'green')
                return jsonify(c_response(200, 'Rating updated'))


            else:
                rating = Ratings(user_id=user.id, manga_id=manga.id, rating=rating_i)
                db.session.add(rating)
                db.session.commit()

                pprint(f'[i] Info: {request.path} - User {user.username} rated {manga.title} with {rating_i} star.', 'green')
                return jsonify(c_response(401, 'Rating not found'))

        else:
            return jsonify(c_response(401, 'Not logged in'))