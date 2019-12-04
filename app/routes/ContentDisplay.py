from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from sqlalchemy.exc import IntegrityError

from app import db
from app.Models import User, Article, Channel
from app.Models import favorite_table
from app.routes.ContentControl import helper_article_list, one_article_query
from app.routes.Admin import one_channel_query

content_display = Blueprint('content_display', __name__)
channel_management = Blueprint('channel_management', __name__)
favorite_management = Blueprint('favorite_management', __name__)


#
# User can only subscribe to non-disabled channels
#
@channel_management.route('/subscribe/<int:cid>')
@jwt_required
def subscribe_to(cid):
    username = get_jwt_identity()
    user_obj = db.session.query(User).filter_by(username=username).first()
    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 401

    channel_obj = one_channel_query(cid)
    if not channel_obj:
        return jsonify({'msg': 'what channel?'}), 404

    try:
        user_obj.subscriptions.append(channel_obj)
        db.session.commit()
        return jsonify({'msg': 'successfully subscribed'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'already subscribed'}), 200


#
# User can only like active articles (not disabled, not requested, not channel disabled)
#
@favorite_management.route('/like/<int:aid>')
@jwt_required
def like(aid):
    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 401

    article_obj = one_article_query(aid)
    if not article_obj:
        return jsonify({'msg': 'what article?'}), 404

    try:
        user_obj.favorites.append(article_obj)
        db.session.commit()
        return jsonify({'msg': 'liked article'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'already liked'}), 200


#
# User may unsubscribe from any channel, including disabled channels
#
@channel_management.route('/unsubscribe/<int:cid>')
@jwt_required
def unsubscribe_from(cid):
    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 401

    channel_obj = Channel.query.get(cid)
    if not channel_obj:
        return jsonify({'msg': 'what channel?'}), 404

    try:
        user_obj.subscriptions.remove(channel_obj)
        db.session.commit()
        return jsonify({'msg': 'successfully unsubscribed'}), 200
    except ValueError:
        return jsonify({'msg': 'user did not subscribe'}), 200


#
# User may unlike any article, including disabled and/or requested articles
#
@favorite_management.route('/unlike/<int:aid>')
@jwt_required
def unlike(aid):
    username: object = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
        return jsonify({'msg': 'who are you?'}), 401

    article_obj = Article.query.get(aid)
    if not article_obj:
        return jsonify({'msg': 'what article?'}), 404

    try:
        user_obj.favorites.remove(article_obj)
        db.session.commit()
        return jsonify({'msg': 'removed like from article'}), 201
    except ValueError:
        return jsonify({'msg': 'article is not liked by user'}), 200


@content_display.route('/subscriptions')
@jwt_required
def get_newest_articles_from_subscribed_channel(limit=20):
    if limit < 1:
        return jsonify([]), 200

    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()

    channel_list = list(map(lambda channel: channel.cid, user_obj.subscriptions))

    it = Article.query.join(User, User.uid == Article.article_author_uid)\
        .join(Channel, Channel.cid == Article.article_channel_cid) \
        .filter(User.is_active) \
        .filter(Channel.cid.in_(channel_list)) \
        .filter(Channel.status.op('&')(4) == 0) \
        .filter(Article.article_status.op('&')(4) == 0) \
        .filter(Article.article_status.op('&')(8) == 0) \
        .order_by(Article.article_created.desc()).limit(limit)

    article_list = helper_article_list(it)

    return jsonify(article_list), 200


@content_display.route('/favorites')
@content_display.route('/favorites/<int:limit>')
@jwt_required
def get_favorites_list(limit=20, page_offset=0):
    if limit < 1:
        return jsonify([]), 200

    username = get_jwt_identity()
    user_obj: User = User.query.filter_by(username=username).first()

    it = Article.query.join(favorite_table)\
        .join(Channel, Channel.cid == Article.article_channel_cid)\
        .join(User, User.uid == Article.article_author_uid)\
        .filter(favorite_table.c.fav_user_uid == user_obj.uid) \
        .filter(Channel.status.op('&')(4) == 0) \
        .filter(User.is_active) \
        .filter(Article.article_status.op('&')(4) == 0) \
        .filter(Article.article_status.op('&')(8) == 0) \
        .order_by(Article.article_created.desc()).limit(limit)

    article_list = helper_article_list(it)

    return jsonify(article_list), 200
