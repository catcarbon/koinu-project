from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.Models import User, Article, Channel, Comment

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


@content_control.route('/article/comments/<int:aid>')
@jwt_required
def get_comments(aid):
    article = Article.query.get(aid)

    if not article:
        return jsonify(msg='what article?'), 400

    comment_list = []
    for comment in article.received_comments:
        comment_dict = {
            'author': comment.sent_by.username,
            'content': comment.body,
            'time': comment.comment_created
        }

        comment_list.append(comment_dict)

    return jsonify(comment_list), 200 if len(comment_list) > 0 else 204


@content_control.route('/article/comment/<int:aid>', methods=['POST'])
@jwt_required
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

    article_obj = Article.query.get(aid)
    if not article_obj:
        return jsonify(msg='what article?'), 400

    comment_obj = Comment(body=comment, comment_article_aid=article_obj.aid)
    user_obj.sent_comments.append(comment_obj)

    db.session.commit()  # error not expected
    return jsonify(msg='comment posted'), 201


@content_control.route('/channel/<int:cid>')
@jwt_required
def get_channel(cid):
    channel = Channel.query.get(cid)

    if not channel:
        return jsonify(msg='what channel?'), 400

    channel_dict = {
        'cid': channel.cid,
        'name': channel.name,
        'summary': channel.description,
        'subscribers': len(channel.subscribers),
        'articles': []
    }

    for article in channel.articles:
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
@jwt_required
def get_channels():
    channel_list = []
    for channel in Channel.query.filter():
        channel_dict = {
            'cid': channel.cid,
            'name': channel.name,
            'summary': channel.description,
            'subscribers': len(channel.subscribers)
        }

        channel_list.append(channel_dict)

    return jsonify(channel_list), 200
