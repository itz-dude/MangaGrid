# -------------- ALLOW SELF EXECUTE --------------- #
import os, sys
sys.path.append(os.getcwd())


# ------------------ IMPORTING -------------------- #
import datetime
import requests

import sqlalchemy as sa

from extensions import db

from manga.models import Mangas, Authors, Genres, Chapters

# -------------------- MODELS --------------------- #

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    main_page = db.Column(db.String(255), default='/latest_updates')
    history_new = db.relationship('HistoryNew', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorites', backref='user', lazy='dynamic')
    ratings = db.relationship('Ratings', backref='user', lazy='dynamic')
    theme = db.Column(db.String(255), default='light')

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.username = self.randomUsername()
        self.main_page = '/latest_updates'

    def randomUsername(self):
        output = [
            requests.get('https://random-word-api.herokuapp.com/word').json(),
            requests.get('https://random-word-api.herokuapp.com/word').json(),
            requests.get('https://random-word-api.herokuapp.com/word').json(),
        ]
        return ''.join([x[0].capitalize() for x in output])

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'main_page': self.main_page
        }

class UsersBehavior():
    def __init__(self, email):
        self.email = email

    def get(self):
        return Users.query.filter_by(email=self.email).first()

    def add(self, password):
        user = Users(self.email, password)
        db.session.add(user)
        db.session.commit()
        return user

    def update(self, user):
        user.updated_at = datetime.datetime.now()
        db.session.commit()
        return user

    def delete(self, user):
        db.session.delete(user)
        db.session.commit()
        return user






history_chapters = db.Table('history_chapters',
    db.Column('history_new_id', db.Integer, db.ForeignKey('history_new.id')),
    db.Column('chapter_id', db.Integer, db.ForeignKey('chapters.id'))
)

class HistoryNew(db.Model):
    __tablename__ = 'history_new'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    chapter = db.relationship('Chapters', secondary=history_chapters, backref='history_new', lazy='dynamic')
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id
        self.updated_at = datetime.datetime.now()

    def __repr__(self):
        return '<History %r>' % self.id

class HistoryBehavior():
    def __init__(self, user_id, manga_id = 0):
        self.user_id = user_id
        self.manga_id = manga_id

    # ---------------- ADDING BEHAVIOR ---------------- #
    def create(self):
        history = HistoryNew(self.user_id, self.manga_id)
        db.session.add(history)
        user = Users.query.filter_by(id=self.user_id).first()
        user.history_new.append(history)
        db.session.commit()

    def add_ch(self, chapter):
        history = self.get()
        if chapter not in history.chapter:
            history.chapter.append(chapter)
            db.session.commit()

    def add_all_ch(self):
        history = self.get()
        history.chapters = []

        manga = Mangas.query.filter_by(id=self.manga_id).first()
        for chapter in sorted(manga.chapters, key=lambda k: k.id, reverse=True):
            self.add_ch(chapter)

        db.session.commit()

    # ---------------- REMOVING BEHAVIOR ---------------- #
    def delete(self):
        Users.query.filter_by(id=self.user_id).first().history.remove(self.get())
        HistoryNew.query.filter(HistoryNew.user_id == self.user_id, HistoryNew.manga_id == self.manga_id).delete()
        db.session.commit()

    def delete_all(self):
        HistoryNew.query.filter(HistoryNew.user_id == self.user_id).delete()
        Users.query.filter_by(id=self.user_id).first().history = []
        db.session.commit()

    def remove_ch(self, chapter):
        history = self.get()
        if chapter in history.chapter:
            history.chapter.remove(chapter)
            db.session.commit()

    def remove_all_ch(self):
        history = self.get()
        history.chapter = []
        db.session.commit()

    # ---------------- GETTING BEHAVIOR ---------------- #
    # ---------------------- SELF ---------------------- #
    def get(self):
        return HistoryNew.query.filter_by(user_id=self.user_id, manga_id=self.manga_id).first()

    def get_all(self):
        return HistoryNew.query.filter_by(user_id=self.user_id).order_by(HistoryNew.updated_at.desc()).all()

    def serialize(self):
        h = self.get()
        return {
            'id': h.id,
            'user_id': h.user_id,
            'manga_id': h.manga_id,
            'chapter': [x.serialize() for x in h.chapter],
            'updated_at': h.updated_at
        }

    def serialize_all(self):
        return [x.serialize() for x in self.get_all()]

    # --------------------- READED --------------------- #
    def get_readed(self):
        return self.get().chapter.all()

    def get_last_readed(self):
        return self.get().chapter.order_by(Chapters.id).first()




class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id
        self.updated_at = datetime.datetime.now()

    def __repr__(self):
        return '<Favorite %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'manga_id': self.manga_id,
            'updated_at': self.updated_at
        }






class Ratings(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, manga_id, rating):
        self.user_id = user_id
        self.manga_id = manga_id
        self.rating = rating
        self.updated_at = datetime.datetime.now()

    def __repr__(self):
        return '<Rating %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'manga_id': self.manga_id,
            'rating': self.rating,
            'updated_at': self.updated_at
        }    



if __name__ == '__main__':
    history = HistoryBehavior(1, 462)
    history.delete_all()
    # history = HistoryNew.query.all()
    # print(history.remove_all_ch())
    # print(history.add_all_ch())
    # print(history.get_readed())
    # print(history.get_last_readed())