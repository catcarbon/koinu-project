from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from sqlalchemy.exc import IntegrityError

from app import db
from app.Models import User, Article, Channel, Comment

admin = Blueprint('admin', __name__)


def check_admin(username):
    user = User.query.filter_by(username=username).filter_by(is_active=True).first()
    if user:
        return user.is_admin()
    return False


@admin.route('/channel/create', methods=['POST'])
@jwt_required
def create_channel():
    if not request.is_json:
        return jsonify(msg='not json'), 400

    name = request.json.get('name')
    if not name:
        return jsonify(msg='missing required channel name'), 400

    description = request.json.get('description')
    is_public = request.json.get('is_public')

    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    channel_obj = Channel(name=name, description=description, is_public=is_public)
    db.session.add(channel_obj)
    try:
        db.session.commit()  # error not expected
        return jsonify(msg='channel created', cid=channel_obj.cid), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg='channel name existed'), 200


@admin.route('/article/delete/<int:aid>', methods=['POST'])
@jwt_required
def delete_article(aid):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    article_obj = Article.query.get(aid=aid)
    if not article_obj:
        return jsonify(msg='what article?'), 404

    if article_obj.is_disabled():
        return jsonify(msg='article already removed'), 200
    else:
        article_obj.set_disabled()
        db.session.add(article_obj)
        db.session.commit()  # error not expected
        return jsonify(msg='article removed'), 200


@admin.route('/article/comments/delete/<int:aid>/<int:coid>')
@jwt_required
def delete_comment(aid, coid):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    comment_obj = Comment.query.filter_by(coid=coid, comment_article_aid=aid).first()
    if not comment_obj:
        return jsonify(msg='no such comment'), 404

    db.session.delete(comment_obj)
    db.session.commit()  # error not expected
    return jsonify(msg='comment deleted'), 200


@admin.route('/channel/delete/<int:cid>', methods=['POST'])
@jwt_required
def delete_channel(cid):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    channel_obj = Channel.query.get(cid)
    if not channel_obj:
        return jsonify(msg='what channel?'), 404

    if channel_obj.is_disabled():
        return jsonify(msg='channel already removed'), 200
    else:
        channel_obj.set_disabled()
        db.session.add(channel_obj)
        db.session.commit()  # error not expected
        return jsonify(msg='channel removed'), 200


@admin.route('/article/post/<int:cid>', methods=['POST'])
@jwt_required
def post_article_to_channel(cid):
    pass


@admin.route('/article/requests')
@admin.route('/article/requests/<int:cid>')
@jwt_required
def get_requests(cid=None):
    pass


@admin.route('/article/accept/<int:aid>')
@jwt_required
def accept_article(aid):
    pass


@admin.route('/article/reject/<int:aid>')
@jwt_required
def reject_article(aid):
    pass
