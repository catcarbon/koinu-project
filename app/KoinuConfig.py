import os
from datetime import timedelta


class KoinuConfig(object):
    # app
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    APP_NAME = 'KoinuProject'
    APP_VERSION = '1.0.0'

    # environment variables
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'random-string-here-please...'

    # sqlalchemy config
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # jwt config
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # flask config
    FLASK_SECRET = SECRET_KEY


class ProductionConfig(KoinuConfig):
    # normal jwt expiry
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(weeks=1)

    DB_USER = 'dp-user'
    DB_PASS = 'randomly...generated...password'
    DB_HOST = 'localhost'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(DB_USER, DB_PASS,
                                                                                   DB_HOST, KoinuConfig.APP_NAME)


class DebugConfig(KoinuConfig):
    DEBUG = True
    DEVELOPMENT = True

    # shorter jwt token expiry for debug
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=5)

    # use root to avoid permission error while performing migrations
    DB_USER = 'root'
    DB_PASS = 'random...string...'
    DB_HOST = 'localhost'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(DB_USER, DB_PASS,
                                                                                   DB_HOST, KoinuConfig.APP_NAME)


DefaultConfig = ProductionConfig()
ActiveConfig = DebugConfig()
