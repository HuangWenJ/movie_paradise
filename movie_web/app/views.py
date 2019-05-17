# -*- coding: utf-8 -*-
from app import app, db
from app.models import User, Post, ROLE_USER, ROLE_ADMIN, Movie
from flask import render_template, flash, redirect, session, url_for, request, g
from sqlalchemy import desc, func
@app.route('/')
def index():
    pagination = Movie.query.paginate(1, per_page=20, error_out=False)
    movies=pagination.items
    return render_template('index.html', movies=movies, pagination=pagination)

@app.route('/page/<page_id>')
def get_movies_by_page(page_id):
    pagination = Movie.query.paginate(int(page_id), per_page=20, error_out=False)
    movies=pagination.items
    return render_template('index.html', movies=movies, pagination=pagination)

@app.route('/movie/<movie_id>')
def movie(movie_id):
    movie = Movie.query.filter_by(id=movie_id).first()
    return render_template('detail.html', movie=movie)

@app.route('/category/<category_name>/page/<page_id>')
def get_movies_by_category(category_name, page_id):
    category = ''
    if category_name == 'fiction':
        category = '%科幻%'
    elif category_name == 'horror':
        category = '%恐怖%'
    elif category_name == 'feature':
        category = '%剧情%'
    elif category_name == 'animation':
        category = '%动画%'
    elif category_name == 'action':
        category = '%动作%'
    elif category_name == 'comedy':
        category='%喜剧%'
    pagination = Movie.query.filter(Movie.categories.like(category)).order_by(Movie.id.asc()).paginate(int(page_id), per_page=20, error_out=False)
    movies=pagination.items
    return render_template('index.html', movies=movies, pagination=pagination)

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
