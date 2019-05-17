# -*- coding: utf-8 -*-

from app import db
ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(60), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    def __repr__(self):
        return '< User % r >' % self.nickname

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
        
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id=db.Column(db.Integer, unique=True)
    title = db.Column(db.String(100))
    translated_title = db.Column(db.String(100))
    upload_date = db.Column(db.Integer)
    year = db.Column(db.Integer)
    country = db.Column(db.String(30))
    categories = db.Column(db.String(30))
    language = db.Column(db.String(30))
    date = db.Column(db.String(30))
    score = db.Column(db.Float)
    length = db.Column(db.String(20))
    director = db.Column(db.String(30))
    star_in = db.Column(db.String(50))
    description = db.Column(db.String(500))
    cover_url = db.Column(db.String(200))
    download_url = db.Column(db.String(200))
    magnet_url = db.Column(db.String(200))
    def __repr__(self):
        return '<Movie %r>' % (self.title)
        
    
    
    
    
    
    
    