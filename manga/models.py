# ------------------ IMPORTING -------------------- #
import datetime

from extensions import db

# -------------------- MODELS --------------------- #

class Manga(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    image = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __init__(self, name, description, image):
        self.name = name
        self.description = description
        self.image = image

    def __repr__(self):
        return f'<Manga {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relation_path = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __init__(self, manga_id, name, relation_path):
        self.manga_id = manga_id
        self.name = name
        self.relation_path = relation_path

    def __repr__(self):
        return f'<Chapter {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'manga_id': self.manga_id,
            'name': self.name,
            'relation_path': self.relation_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }