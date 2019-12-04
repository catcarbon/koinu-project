from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from sqlalchemy.exc import IntegrityError, DataError

from app import db, limit_payload_length
from app.Models import User, Article, Channel, Comment

admin = Blueprint('admin', __name__)


def check_admin(username):
    user = User.query.filter_by(username=username).filter_by(is_active=True).first()
    if user:
        return user.is_admin()
    return False


#
# Return a single channel which isn't disabled.
#
def one_channel_query(cid):
    channel = Channel.query.filter(Channel.status.op('&')(4) == 0).filter_by(cid=cid).first()
    return channel


@admin.route('/channel/create', methods=['POST'])
@jwt_required
@limit_payload_length(Channel.MAX_NAME_LENGTH + Channel.MAX_DESCRIPTION_LENGTH + 100)
def create_channel():
    if not request.is_json:
        return jsonify(msg='not json'), 400

    name = request.json.get('name')
    if not name:
        return jsonify(msg='missing required channel name'), 400

    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    description = request.json.get('description')
    is_public = request.json.get('is_public')

    channel_obj = Channel(name=name, description=description, is_public=is_public)
    db.session.add(channel_obj)

    ret_json, ret_code = {'msg': 'channel created'}, 201
    try:
        ret_json['cid'] = channel_obj.cid
        db.session.commit()
    except IntegrityError:
        ret_json['msg'], ret_code = 'channel name existed', 400
        db.session.rollback()
    except DataError:
        ret_json['msg'] = 'requested name and/or description too long'
        ret_json['max_name'], ret_json['max_description'] = Channel.MAX_NAME_LENGTH, Channel.MAX_DESCRIPTION_LENGTH
        ret_code = 413
        db.session.rollback()
    finally:
        return jsonify(ret_json), ret_code


@admin.route('/article/delete/<int:aid>', methods=['POST', 'DELETE'])
@jwt_required
def delete_article(aid):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    article_obj = Article.query.get(aid=aid)
    if not article_obj:
        return jsonify(msg='what article?'), 404

    if article_obj.is_disabled():
        return jsonify(msg='article already removed'), 400
    else:
        article_obj.set_disabled()
        db.session.add(article_obj)
        db.session.commit()  # error not expected
        return jsonify(msg='article removed'), 200


#
# Comment are outright deleted from database, not disabled.
#
@admin.route('/article/comments/delete/<int:aid>/<int:coid>', methods=['POST', 'DELETE'])
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


@admin.route('/channel/delete/<int:cid>', methods=['POST', 'DELETE'])
@jwt_required
def delete_channel(cid):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    channel_obj = Channel.query.get(cid)
    if not channel_obj:
        return jsonify(msg='what channel?'), 404

    if channel_obj.is_disabled():
        return jsonify(msg='channel already removed'), 400
    else:
        channel_obj.set_disabled()
        db.session.add(channel_obj)
        db.session.commit()  # error not expected
        return jsonify(msg='channel removed'), 200


@admin.route('/channel/post/<int:cid>', methods=['POST'])
@jwt_required
@limit_payload_length(Article.MAX_CONTENT_LENGTH + Article.MAX_TITLE_LENGTH + 100)
def post_article_to_channel(cid):
    if not request.is_json:
        return jsonify({'msg': 'Not json'}), 400

    title = request.json.get('title')
    content = request.json.get('content')
    if not title or not content:
        return jsonify(msg='missing title or content'), 400

    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
        return jsonify(msg='who are you?'), 400

    channel = one_channel_query(cid)
    if not channel:
        return jsonify(msg='what channel?'), 404

    # admin user can post article without approval
    article_obj = Article(title=title, content=content, article_author_uid=user_obj.uid,
                          article_channel_cid=cid, article_status=1 if user_obj.is_admin() else 9)
    db.session.add(article_obj)

    try:
        db.session.commit()
        return jsonify(msg='article requested', aid=article_obj.aid)
    except DataError:
        db.session.rollback()
        return jsonify(msg='requested title and/or content too long',
                       max_title=Article.MAX_TITLE_LENGTH, max_content=Article.MAX_CONTENT_LENGTH), 413


#
# Return active requests of active channels.
#
@admin.route('/article/requests')
@admin.route('/article/requests/<int:cid>')
@jwt_required
def get_requests(cid=None):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    request_it = []
    if cid:
        channel = one_channel_query(cid)
        if not channel:
            return jsonify(msg='what channel?'), 404

        requests_it = Article.query.filter(Article.article_status.op('&')(4) == 0)\
                                   .filter(Article.article_status.op('&')(8) != 0)\
                                   .filter_by(article_channel_cid=cid)
    else:
        requests_it = Article.query.join(Channel).filter(Channel.status.op('&')(4) == 0)\
                                                 .filter(Article.article_status.op('&')(4) == 0)\
                                                 .filter(Article.article_status.op('&')(8) != 0)

    requested_articles = []
    for article in requests_it:
        article_dict = {
            'aid': article.aid,
            'cid': article.article_channel_cid,
            'title': article.title,
            'author': article.author.username,
            'publish_time': article.article_created,
            'content': article.content
        }

        requested_articles.append(article_dict)

    return jsonify(requested_articles), 200


@admin.route('/article/accept/<int:aid>', methods=['POST'])
@jwt_required
def accept_article(aid):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    article = Article.query.get(aid)
    if not article:
        return jsonify(msg='what article?'), 404

    if article.is_requested() and not article.is_disabled():
        article.toggle_requested()
        db.session.add(article)
        db.session.commit()
        return jsonify(msg='requested article accepted'), 200

    msg = 'requested article already accepted'
    if article.is_disabled():
        msg = 'requested article has been removed'  # currently no api to restore article

    return jsonify(msg=msg), 400


@admin.route('/article/reject/<int:aid>', methods=['POST'])
@jwt_required
def reject_article(aid):
    username = get_jwt_identity()
    if not check_admin(username):
        return jsonify(msg='unauthorized'), 401

    article = Article.query.get(aid)
    if not article:
        return jsonify(msg='what article?'), 404

    if article.is_requested() and not article.is_disabled():
        # retain requested flag so it shows that the article is rejected on request, not disabled later
        article.toggle_disabled()
        db.session.add(article)
        db.session.commit()
        return jsonify(msg='requested article rejected'), 200

    msg = 'requested article already accepted, please use /api/article/delete to remove article'
    if article.is_disabled():
        msg = 'requested article already removed'

    return jsonify(msg=msg), 400
