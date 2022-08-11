# -------------- ALLOW SELF EXECUTE --------------- #
import os, sys
sys.path.append(os.getcwd())


# ------------------ IMPORTING -------------------- #
import datetime
import requests

from extensions import db
from tools.tools import BehaviorStructure

from manga.models import Mangas, Chapters

# -------------------- MODELS --------------------- #

# -------------------- USERS --------------------- #
class LoginAttempts(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(200), db.ForeignKey('users.email'))
    attempts = db.Column(db.Integer)
    last_attempt = db.Column(db.DateTime)

    def __init__(self, user_email, attempts, last_attempt):
        self.user_email= user_email
        self.attempts = attempts
        self.last_attempt = last_attempt

    def __repr__(self):
        return f'<LoginAttempts {self.id} - {self.user_id}>'




# -------------------- USERS --------------------- #
class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    main_page = db.Column(db.String(255), default='/latest_updates')
    theme = db.Column(db.String(255), default='light')

    # -- relationships -- #
    favorites = db.relationship('Favorites', backref='user', lazy='dynamic')
    history = db.relationship('History', backref='user', lazy='dynamic')
    ratings = db.relationship('Ratings', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.username = self.randomUsername()

    def randomUsername(self):
        output = [
            requests.get('https://random-word-api.herokuapp.com/word').json(),
            requests.get('https://random-word-api.herokuapp.com/word').json(),
            requests.get('https://random-word-api.herokuapp.com/word').json(),
        ]
        return ''.join([x[0].capitalize() for x in output])

    def __repr__(self):
        return '<User %r>' % self.username

    def __name__(self):
        return 'User'

    def serialize(self):
        return {
            'user_id': self.id,
            'user_active': self.active,
            'user_username': self.username,
            'user_email': self.email,
            'user_created_at': self.created_at,
            'user_updated_at': self.updated_at,
            'user_main_page': self.main_page,
            'user_theme': self.theme
        }





# ----------------- NOTIFICATIONS ------------------ #
class Notifications(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(75), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    readed = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(255), default='icon-notification')
    image = db.Column(db.String(500))
    href_slug = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # -- relationships -- #
    user = db.relationship('Users', backref=db.backref('notifications', lazy='dynamic'))

    def __init__(self, user_id, title, message, icon = 'icon-notification', image = None, href_slug = None):
        self.user_id = user_id
        self.title = title
        self.message = message
        self.icon = icon
        self.image = image
        self.href_slug = href_slug

    def __repr__(self):
        return f'<Notifications {self.id} - {self.user_id}>'

    def serialize(self):
        return {
            'notification_id': self.id,
            'notification_user_id': self.user_id,
            'notification_icon': self.icon,
            'notification_title': self.title,
            'notification_message': self.message,
            'notification_readed': self.readed,
            'notification_image': self.image,
            'notification_href_slug': self.href_slug,
            'notification_created_at': self.created_at
        }

    @staticmethod
    def send_notification(user_id, title, message, icon = 'icon-notification', image = None, href_slug = None):
        """
        Send a notification to a user. Note that this function will not check if the user exists
        or if the notification already exists and it wont commit the changes to the database.
        """
        notification = Notifications(user_id, title, message, icon, image, href_slug)
        db.session.add(notification)
        return notification  





# -------------------- HISTORY --------------------- #
history_fk_chapter = db.Table('history_fk_chapter',
    db.Column('history_id', db.Integer, db.ForeignKey('history.id')),
    db.Column('chapter_id', db.Integer, db.ForeignKey('chapters.id'))
)

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id

    def __repr__(self):
        return '<History %r>' % self.id

    def __name__(self):
        return 'History'

    def serialize(self):
        return {
            'history_id': self.id,
            'history_user_id': self.user_id,
            'history_manga_id': self.manga_id,
            'history_created_at': self.created_at,
            'history_updated_at': self.updated_at
        }





# -------------------- FAVORITES --------------------- #
class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id

    def __repr__(self):
        return '<Favorite %r>' % self.id

    def __name__(self):
        return 'Favorite'

    def serialize(self):
        return {
            'favorites_id': self.id,
            'favorites_user_id': self.user_id,
            'favorites_manga_id': self.manga_id,
            'favorites_created_at': self.created_at
        }







# -------------------- RATINGS --------------------- #
class Ratings(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, user_id, manga_id, rating):
        self.user_id = user_id
        self.manga_id = manga_id
        self.rating = rating

    def __repr__(self):
        return '<Rating %r>' % self.id

    def __name__(self):
        return 'Rating'

    def serialize(self):
        return {
            'ratings_id': self.id,
            'ratings_user_id': self.user_id,
            'ratings_manga_id': self.manga_id,
            'ratings_rating': self.rating,
            'ratings_created_at': self.created_at,
            'ratings_updated_at': self.updated_at
        }    





if __name__ == '__main__':
    ...