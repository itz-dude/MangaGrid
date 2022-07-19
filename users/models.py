# ------------------ IMPORTING -------------------- #
import datetime
import requests

from extensions import db


# -------------------- MODELS --------------------- #

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    # liked_manga = db.relationship('LikedManga', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

        if self.username == '':
            self.username = self.randomUsername

    @property
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
            'updated_at': self.updated_at
        }