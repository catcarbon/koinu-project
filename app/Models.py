from enum import Enum

from argon2.exceptions import VerifyMismatchError
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

from sqlalchemy.sql import func

from app import db, argon2
from app.KoinuConfig import ActiveConfig as Config


subscription_table = db.Table('Subscription',
                              db.Column('user_uid', db.Integer, db.ForeignKey('User.uid')),
                              db.Column('channel_cid', db.Integer, db.ForeignKey('Channel.cid')))

favorite_table = db.Table('Favorite',
                          db.Column('user_uid', db.Integer, db.ForeignKey('User.uid')),
                          db.Column('article_aid', db.Integer, db.ForeignKey('Article.aid')))


class UserRole(Enum):
    Admin = 1
    Editor = 2
    Reader = 4


class User(db.Model):
    __tablename__ = 'User'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.SmallInteger, default=4, server_default="4", nullable=False)
    is_active = db.Column(db.Boolean, default=1, server_default="1", nullable=False)

    subscribed_to = db.relationship('subscribed_to', secondary=subscription_table, back_populates='subscribed_by')
    favorites = db.relationship('favorites', secondary=favorite_table, back_populates='favorited_by')

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

        user = User.query.get(data['uid'])
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
        return self.role & UserRole.Admin.value != 0

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Channel(db.Model):
    __tablename__ = 'Channel'
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), index=True, nullable=False)
    description = db.Column(db.Text)
    channel_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    channel_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    is_public = db.Column(db.Boolean, default=1, server_default="1", nullable=False)
    channel_admin_uid = db.Column(db.Integer, db.ForeignKey('User.uid'))

    subscribed_by = db.relationship('subscribed_by', secondary=subscription_table, back_populates='subscribed_to')


class ArticleStatus:
    Public = 1
    Private = 2
    Disabled = 4


class Article(db.Model):
    __tablename__ = 'Article'
    aid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), index=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    article_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    article_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    article_status = db.Column(db.SmallInteger, default=1, server_default="1", nullable=False)
    article_author_uid = db.Column(db.Integer, db.ForeignKey('User.uid'))
    article_channel_cid = db.Column(db.Integer, db.ForeignKey('Channel.cid'))

    favorited_by = db.relationship('favorited_by', secondary=favorite_table, back_populates='favorites')

    def __repr__(self):
        return '<Article {}: {}>'.format(self.aid, self.title)
