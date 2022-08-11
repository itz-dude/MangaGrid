# ---------------- DEFAULT IMPORTS ---------------- #

import datetime

from flask import Blueprint, jsonify, session, request
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from tools.tools import c_response, pprint, check_email

from manga.models import Sources, Mangas, Chapters
from users.models import Ratings, Users, History, Favorites, LoginAttempts, Notifications





# ---------------- STARTING ROUTE ----------------- #

users = Blueprint('users', __name__)


# --------------------- TOOLS --------------------- #

def login_required(f):
    def wrap(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        else:
            return c_response(401, 'Not logged in')
    return wrap



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

            user = Users.query.filter_by(email=email).first()
            notification = Notifications(user.id, 'Welcome to Manga Reader', 'Thank you for using our site!')
            db.session.add(notification)
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


@login_required
@users.route('/session/get_profile')
def session_get_profile():
    user = Users.query.filter_by(email=session['email']).first()

    pprint(f'[i] Info: {request.path} - User {user.email} requested profile.', 'green')
    return jsonify(c_response(200, 'Profile send', user.serialize()))


@login_required
@users.route('/session/update/<section>', methods = ['POST'])
def session_update_info(section):
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
@login_required
@users.route('/session/history')
def session_history():
    user = Users.query.filter_by(email=session['email']).first()
    data = []
    for item in user.history.order_by(History.updated_at.desc()).all():
        current_history = user.history.filter_by(manga_id=item.manga_id).first()

        if current_history.chapters.count() > 0:
            output = current_history.serialize() | \
                current_history.mangas.serialize() | \
                {'manga_source': current_history.mangas.sources.slug} | \
                current_history.chapters.order_by(Chapters.id.desc()).first().serialize()
            data.append(output)

    data = sorted(data, key=lambda k: k['history_updated_at'], reverse=True)

    pprint(f'[i] Info: {request.path} - User {user.username} requested history.', 'green')
    return jsonify(c_response(200, 'History sent', data))


@login_required
@users.route('/session/history/<string:source_slug>/<string:manga_slug>/<string:param>')
def session_history_manga(source_slug = None, manga_slug = None, param = None):
    if not source_slug or not manga_slug:
        return jsonify(c_response(401, 'Missing parameters'))

    user = Users.query.filter_by(email=session['email']).first()
    try:
        filter = []

        if param == 'latest':
            filter.append(History.updated_at.desc())

        history = user.history.join(Mangas).join(Sources).filter(Mangas.slug==manga_slug, Sources.slug==source_slug).order_by(*filter).first()

        data = {}
        if history and history.chapters.count() > 0:
            data = history.serialize() | \
                history.mangas.serialize() | \
                history.chapters.order_by(Chapters.id.desc()).first().serialize()

            return jsonify(c_response(200, 'History sent', data))

        else:
            raise Exception()

    except:
        return jsonify(c_response(401, 'History not found'))

@login_required
@users.route('/session/history/reset', methods = ['POST'])
@users.route('/session/history/reset/<string:manga_slug>', methods = ['POST'])
def session_history_reset(manga_slug = None):
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

@login_required
@users.route('/session/history/<string:source_slug>/<string:manga_slug>/set/<string:option>', methods = ['POST'])
def session_history_set(source_slug = None, manga_slug = None, option = None):
    session['email'] = 'admin@admin.com'


    if not source_slug or not manga_slug or not option:
        return jsonify(c_response(401, 'Invalid parameters'))

    user = Users.query.filter_by(email=session['email']).first()
    manga = Mangas.query.join(Sources).filter(Mangas.slug==manga_slug, Sources.slug==source_slug).first()
    if not manga:
        return jsonify(c_response(401, 'Manga not found'))

    history = user.history.filter_by(manga_id = manga.id).first()
    if not history:
        history = History(user_id = user.id, manga_id = manga.id)
        db.session.add(history)
        db.session.commit()


    if option == 'read_all':
        history.chapters = [chapter for chapter in manga.chapters]
        history.updated_at = datetime.datetime.now()
        db.session.commit()
        return jsonify(c_response(200, 'History updated', {'action': option}))

    elif option == 'unread_all':
        history.chapters = []
        history.updated_at = datetime.datetime.now()
        db.session.commit()
        return jsonify(c_response(200, 'History updated', {'action': option}))

    else:
        return jsonify(c_response(401, 'Invalid parameters'))


# ------------------- FAVORITES -------------------- #
@login_required
@users.route('/session/favorite/filter/<filter>')
def session_favorites(filter = 'manga_title'):
    if request.method == 'GET':
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

@login_required
@users.route('/session/favorite/<string:source>/<string:manga>', methods = ['GET', 'POST'])
def session_favorites_manga(source = None, manga = None):
    if not manga or not source:
        return jsonify(c_response(401, 'Missing parameters'))

    user = Users.query.filter_by(email=session['email']).first()
    manga = Mangas.query.join(Sources).filter(Mangas.slug==manga, Sources.slug==source).first()

    if request.method == 'GET':
        if user.favorites.filter_by(manga_id = manga.id).first():
            pprint(f'[i] Info: {request.path} - {user.username} requested in his favorites and have.', 'green')
            return jsonify(c_response(200, 'Sended', {'status': 'true'}))

        else:
            pprint(f'[i] Info: {request.path} - {user.username} requested in his favorites and have not.', 'green')
            return jsonify(c_response(200, 'Sended', {'status': 'false'}))

    elif request.method == 'POST':
        if user.favorites.filter_by(manga_id = manga.id).first():
            favorite = user.favorites.filter_by(manga_id = manga.id).first()
            user.favorites.remove(favorite)
            db.session.delete(favorite)
            db.session.commit()
            pprint(f'[i] Info: {request.path} - Removed manga {manga} from {user.username} favorites.', 'green')
            return jsonify(c_response(200, 'Manga already in favorites. Removed', {'operation': 'removed'}))
            

        else:
            favorite = Favorites(user_id = user.id, manga_id = manga.id)
            db.session.add(favorite)
            db.session.commit()
            user.favorites.append(favorite)
            db.session.commit()
            pprint(f'[i] Info: {request.path} - Added manga {manga} to {user.username} favorites.', 'green')
            return jsonify(c_response(200, 'Manga added to favorites', {'operation': 'added'}))


# -------------------- RATING --------------------- #
# @login_required
@users.route('/session/rating/<string:source>/<string:manga>')
@users.route('/session/rating/<string:source>/<string:manga>/<int:rating_i>', methods = ['POST'])
def session_rating(source = None, manga = None, rating_i = None):
    if not manga or not source:
        return jsonify(c_response(401, 'Missing parameters'))

    user = Users.query.filter_by(email=session['email']).first()
    manga = Mangas.query.join(Sources).filter(Mangas.slug==manga, Sources.slug==source).first()
    rating = user.ratings.filter_by(manga_id=manga.id).first()

    if request.method == 'GET':
        if rating:
            pprint(f'[i] Info: {request.path} - Rating of {manga.title} from {user.username}', 'green')
            return jsonify(c_response(200, 'Rating sent', rating.rating))

        else:
            pprint(f'[i] Info: {request.path} - User {user.username} havent rated {manga.title} yet.', 'green')
            return jsonify(c_response(200, 'Not rated', 0))

    elif request.method == 'POST':
        if not rating:
            rating = Ratings(user_id=user.id, manga_id=manga.id, rating=rating_i)
            db.session.add(rating)
            db.session.commit()

            pprint(f'[i] Info: {request.path} - User {user.username} rated {manga.title} with {rating_i} star.', 'green')
            return jsonify(c_response(200, 'Rating added', {'action': 'added'}))

        elif rating.rating == rating_i:
            db.session.delete(rating)
            db.session.commit()
            pprint(f'[i] Info: {request.path} - User {user.username} removed his rating of {manga.title}.', 'green')
            return jsonify(c_response(200, 'Rating removed', {'action': 'removed'}))

        else:
            rating.rating = rating_i
            db.session.commit()

            pprint(f'[i] Info: {request.path} - User {user.username} rated {manga.title} with {rating_i} star.', 'green')
            return jsonify(c_response(200, 'Rating updated', {'action': 'changed'}))

# ----------------- NOTIFICATIONS ----------------- #
@login_required
@users.route('/session/notification/', methods = ['GET'])
@users.route('/session/notification/<int:id>', methods = ['GET'])
def session_notifications(id = None):
    user = Users.query.filter_by(email=session['email']).first()

    filter = []
    if id:
        filter.append(Notifications.id == id)

    notif_query = user.notifications
    notifications = {
        'new_notifications': len(notif_query.filter_by(readed=False).all()),
        'notifications':[n.serialize() for n in notif_query.filter(*filter).order_by(Notifications.id.desc()).all()]
    }

    if notifications:
        pprint(f'[i] Info: {request.path} - Notifications of {user.username}', 'green')
        return jsonify(c_response(200, 'Notifications sent', notifications))

    else:
        pprint(f'[i] Info: {request.path} - Notifications of {user.username}', 'green')
        return jsonify(c_response(200, 'Notifications not found', []))

@login_required
@users.route('/session/notification/<string:option>', methods = ['POST'])
def session_notifications_mark_readed(option):
    user = Users.query.filter_by(email=session['email']).first()

    if option in ['mark_readed', 'mark_all_readed']:
        input_json = request.get_json()

        filter = []

        if option == 'mark_readed':
            filter.append(Notifications.id == input_json['notification_id'])

        for notification in user.notifications.filter(*filter):
            notification.readed = True
            db.session.commit()

        return jsonify(c_response(200, 'Notifications readed'))

    elif option == 'delete_all':
        for notification in user.notifications.all():
            db.session.delete(notification)
            db.session.commit()

        return jsonify(c_response(200, 'Notifications deleted'))