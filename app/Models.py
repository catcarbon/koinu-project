from enum import Enum

from argon2.exceptions import VerifyMismatchError
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

from sqlalchemy.sql import func

from app import db, argon2
from app.KoinuConfig import ActiveConfig as Config


subscription_table = db.Table('subscriptions',
                              db.Column('sub_user_uid', db.Integer, db.ForeignKey('User.uid'), primary_key=True),
                              db.Column('sub_channel_cid', db.Integer, db.ForeignKey('Channel.cid'), primary_key=True))

favorite_table = db.Table('favorites',
                          db.Column('fav_user_uid', db.Integer, db.ForeignKey('User.uid'), primary_key=True),
                          db.Column('fav_article_aid', db.Integer, db.ForeignKey('Article.aid'), primary_key=True))


class Comment(db.Model):
    __tablename__ = 'comments'
    BODY_MAX_LENGTH = 255
    coid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.Text(length=BODY_MAX_LENGTH), nullable=False)
    comment_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    comment_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    comment_user_uid = db.Column(db.Integer, db.ForeignKey('User.uid'), nullable=False)
    comment_article_aid = db.Column(db.Integer, db.ForeignKey('Article.aid'), nullable=False)


class UserRole(Enum):
    Admin = 1
    Editor = 2
    Reader = 4


class User(db.Model):
    __tablename__ = 'User'
    MAX_USERNAME_LENGTH = 64
    PASSWORD_HASH_LENGTH = 128
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(MAX_USERNAME_LENGTH), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(PASSWORD_HASH_LENGTH))
    role = db.Column(db.SmallInteger, default=4, server_default="4", nullable=False)
    is_active = db.Column(db.Boolean, default=1, server_default="1", nullable=False)

    subscriptions = db.relationship('Channel', secondary=subscription_table, lazy='subquery',
                                    backref=db.backref('subscribers', lazy=True))
    favorites = db.relationship('Article', secondary=favorite_table, lazy='subquery',
                                backref=db.backref('liked_by', lazy=True))
    published_articles = db.relationship('Article', lazy='subquery',
                                         backref=db.backref('author', lazy=True))
    sent_comments = db.relationship('Comment', lazy='subquery',
                                    backref=db.backref('sent_by', lazy=True))

    def __init__(self, username):
        self.username = username

    def generate_token(self, expiration=600):
        s = Serializer(Config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'uid': self.uid})

    @staticmethod
    def verify_token(token):
        s = Serializer(Config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = User.query.get(data['username'])
        return user

    def get_id(self):
        return self.uid

    def set_password(self, password):
        self.password_hash = argon2.hash(password)

    def check_password(self, password):
        try:
            argon2.verify(self.password_hash, password)
            if argon2.check_needs_rehash(self.password_hash):
                self.password_hash = argon2.hash(password)
            return True
        except VerifyMismatchError:
            return False

    def check_has_role(self, role_enum):
        if role_enum in UserRole:
            return self.role & role_enum.value != 0
        return False

    def is_admin(self):
        return self.check_has_role(UserRole.Admin)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class ChannelStatus(Enum):
    Public = 1
    Private = 2
    Disabled = 4


class Channel(db.Model):
    __tablename__ = 'Channel'
    MAX_NAME_LENGTH = 32
    MAX_DESCRIPTION_LENGTH = 255
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), index=True, unique=True, nullable=False)
    description = db.Column(db.Text(MAX_DESCRIPTION_LENGTH))
    channel_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    channel_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    status = db.Column(db.SmallInteger, default=1, server_default="1", nullable=False)
    channel_admin_uid = db.Column(db.Integer, db.ForeignKey('User.uid'))

    articles = db.relationship('Article', lazy='subquery',
                               backref=db.backref('channel', lazy=True))

    def check_has_status(self, status_enum):
        if status_enum in ChannelStatus:
            return self.status & status_enum.value != 0
        return False

    def is_disabled(self):
        return self.check_has_status(ChannelStatus.Disabled)

    def set_disabled(self):
        self.status |= ChannelStatus.Disabled.value

    def toggle_disabled(self):
        self.status ^= ChannelStatus.Disabled.value

    def __repr__(self):
        return '<Channel {}: {}>'.format(self.cid, self.name)


class ArticleStatus(Enum):
    Public = 1
    Private = 2
    Disabled = 4
    Requested = 8
    RejectedRequest = 12


class Article(db.Model):
    __tablename__ = 'Article'
    MAX_TITLE_LENGTH = 64
    MAX_CONTENT_LENGTH = 65535
    aid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(MAX_TITLE_LENGTH), index=True, nullable=False)
    content = db.Column(db.Text(MAX_CONTENT_LENGTH), nullable=False)
    article_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    article_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    article_status = db.Column(db.SmallInteger, default=9, server_default="9", nullable=False)
    article_author_uid = db.Column(db.Integer, db.ForeignKey('User.uid'))
    article_channel_cid = db.Column(db.Integer, db.ForeignKey('Channel.cid'))

    received_comments = db.relationship('Comment', lazy='subquery',
                                        backref=db.backref('posted_on', lazy=True))

    def check_has_status(self, status_enum):
        if status_enum in ArticleStatus:
            return self.article_status & status_enum.value != 0
        return False

    def is_public(self):
        return self.check_has_status(ArticleStatus.Public)

    def is_private(self):
        return self.check_has_status(ArticleStatus.Private)

    def is_requested(self):
        return self.check_has_status(ArticleStatus.Requested)

    def toggle_requested(self):
        self.article_status ^= ArticleStatus.Requested.value

    def is_disabled(self):
        return self.check_has_status(ArticleStatus.Disabled)

    def set_disabled(self):
        self.article_status |= ArticleStatus.Disabled.value

    def toggle_disabled(self):
        self.article_status ^= ArticleStatus.Disabled.value

    def __repr__(self):
        return '<Article {}: {}>'.format(self.aid, self.title)

