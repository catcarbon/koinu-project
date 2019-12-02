from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from app import db
from app.Models import User, Article, Channel
from app.Models import favorite_table, subscription_table

content_control = Blueprint('content_control', __name__)


@content_control.route('/article/<int:aid>')
@jwt_required
def get_article(aid):
    article = Article.query.get(aid)

    if not article:
        return jsonify(msg='what article?'), 400

    article_dict = {
        'aid': article.aid,
        'title': article.title,
        'author': article.author.username,
        'publish_time': article.article_created,
        'content': article.content
    }

    return jsonify(article_dict), 200


@content_control.route('/article/<int:aid>/comments')
@jwt_required
def get_comments(aid):
    article = Article.query.get(aid)

    Article.query.filter(Article.aid == 1).all()
