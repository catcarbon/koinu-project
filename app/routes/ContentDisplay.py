from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from sqlalchemy.exc import IntegrityError

from app import db
from app.Models import User, Article, Channel

content_display = Blueprint('content_display', __name__)
channel_management = Blueprint('channel_management', __name__)
favorite_management = Blueprint('favorite_management', __name__)


@channel_management.route('/subscribe/<int:cid>')
@jwt_required
def subscribe_to(cid):
    username = get_jwt_identity()
    user_obj = db.session.query(User).filter_by(username=username).first()
    channel_obj = db.session.query(Channel).get(cid)

    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 400
    if not channel_obj:
        return jsonify({'msg': 'what channel?'}), 400

    try:
        user_obj.subscriptions.append(channel_obj)
        db.session.commit()
        return jsonify({'msg': 'successfully subscribed'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'already subscribed'}), 200


@favorite_management.route('/like/<int:aid>')
@jwt_required
def like(aid):
    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    article_obj = Article.query.get(aid)

    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 400
    if not article_obj:
        return jsonify({'msg': 'what article?'}), 400

    try:
        user_obj.favorites.append(article_obj)
        db.session.commit()
        return jsonify({'msg': 'liked article'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'already liked'}), 200


@channel_management.route('/unsubscribe/<int:cid>')
@jwt_required
def unsubscribe_from(cid):
    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    channel_obj = Channel.query.get(cid)

    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 400
    if not channel_obj:
        return jsonify({'msg': 'what channel?'}), 400

    try:
        user_obj.subscriptions.remove(channel_obj)
        db.session.commit()
        return jsonify({'msg': 'successfully unsubscribed'}), 200
    except ValueError:
        return jsonify({'msg': 'user did not subscribe'}), 200


@favorite_management.route('/unlike/<int:aid>')
@jwt_required
def unlike(aid):
    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    article_obj = Article.query.get(aid)

    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 400
    if not article_obj:
        return jsonify({'msg': 'what article?'}), 400

    try:
        user_obj.favorites.remove(article_obj)
        db.session.commit()
        return jsonify({'msg': 'removed like from article'}), 201
    except ValueError:
        return jsonify({'msg': 'article is not liked by user'}), 200


@content_display.route('/subscriptions')
@jwt_required
def get_newest_articles_from_subscribed_channel(limit=20):
    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()

    channel_map = map(lambda channel: channel.cid, user_obj.subscriptions)

    it = Article.query.filter(Article.article_channel_cid.in_(channel_map))\
                      .order_by(Article.article_created.desc()).limit(limit)

    article_list = []
    for article in it:
        article_dict = {
            'aid': article.aid,
            'title': article.title,
            'author': article.author.username,
            'publish_time': article.article_created,
            'content': article.content
        }
        article_list.append(article_dict)

    return jsonify(article_list), 200


@content_display.route('/favorites/<int:page_offset>')
@jwt_required
def get_favorites_list(limit=20, page_offset=0):
    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()

    # TODO
