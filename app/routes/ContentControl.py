from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import DataError

from app import db, limit_payload_length
from app.Models import User, Article, Channel, Comment
from app.routes.Admin import one_channel_query

content_control = Blueprint('content_control', __name__)


#
# Return a single article which isn't disabled or its channel disabled.
#
def one_article_query(aid):
    article = Article.query.join(Channel).join(User, User.uid == Article.article_author_uid)\
                           .filter(Article.aid == aid) \
                           .filter(Channel.status.op('&')(4) == 0) \
                           .filter(User.is_active) \
                           .filter(Article.article_status.op('&')(4) == 0) \
                           .filter(Article.article_status.op('&')(8) == 0).first()

    return article


@content_control.route('/article/<int:aid>')
def get_article(aid):
    article = one_article_query(aid)
    if not article:
        return jsonify(msg='what article?'), 404

    article_dict = {
        'aid': article.aid,
        'title': article.title,
        'author': article.author.username,
        'publish_time': article.article_created,
        'content': article.content
    }

    return jsonify(article_dict), 200


#
# Removed comments are being deleted from the database in current implementation.
# However, comments made by a later disabled user are not deleted, so these are filtered out.
#
@content_control.route('/article/comments/<int:aid>')
def get_comments(aid):
    article = one_article_query(aid)
    if not article:
        return jsonify(msg='what article?'), 404

    comments = Comment.query.join(User).filter(Comment.comment_article_aid == aid)\
                                       .filter(User.is_active)

    comment_list = []
    for comment in comments:
        comment_dict = {
            'coid': comment.coid,
            'author': comment.sent_by.username,
            'content': comment.body,
            'time': comment.comment_created
        }

        comment_list.append(comment_dict)

    return jsonify(comment_list), 200


@content_control.route('/article/comment/<int:aid>', methods=['POST'])
@jwt_required
@limit_payload_length(Comment.BODY_MAX_LENGTH + 100)
def post_comment(aid):
    if not request.is_json:
        return jsonify({'msg': 'Not json'}), 400

    comment = request.json.get('comment')
    if not comment:
        return jsonify(msg='empty comment'), 400

    username = get_jwt_identity()
    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
        return jsonify(msg='who are you?'), 400

    article_obj = one_article_query(aid)
    if not article_obj:
        return jsonify(msg='what article?'), 404

    comment_obj = Comment(body=comment, comment_article_aid=article_obj.aid)
    user_obj.sent_comments.append(comment_obj)

    try:
        db.session.commit()
        return jsonify(msg='comment posted'), 201
    except DataError:
        db.session.rollback()
        return jsonify(msg='comment too long', max=Comment.BODY_MAX_LENGTH), 413


@content_control.route('/channel/<int:cid>')
def get_channel(cid):
    channel = one_channel_query(cid)
    if not channel:
        return jsonify(msg='what channel?'), 404

    channel_dict = {
        'cid': channel.cid,
        'name': channel.name,
        'summary': channel.description,
        'subscribers': len(channel.subscribers),
        'articles': []
    }

    articles = Article.query.join(Channel).join(User, User.uid == Article.article_author_uid) \
                            .filter(Channel.cid == cid) \
                            .filter(User.is_active) \
                            .filter(Article.article_status.op('&')(4) == 0) \
                            .filter(Article.article_status.op('&')(8) == 0)

    for article in articles:
        article_dict = {
            'aid': article.aid,
            'title': article.title,
            'author': article.author.username,
            'publish_time': article.article_created,
            'content': article.content
        }

        channel_dict['articles'].append(article_dict)

    return jsonify(channel_dict), 200


@content_control.route('/channels')
def get_channels():
    channel_list = []
    for channel in Channel.query.filter(Channel.status.op('&')(4) == 0):
        channel_dict = {
            'cid': channel.cid,
            'name': channel.name,
            'summary': channel.description,
            'subscribers': len(channel.subscribers)
        }

        channel_list.append(channel_dict)

    return jsonify(channel_list), 200
