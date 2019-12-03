from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from importlib import import_module

from argon2 import PasswordHasher

from app.KoinuConfig import ActiveConfig as Config

jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
argon2 = PasswordHasher()
blacklist = set()

import_module('app.Models')


def create_app():
    _app = Flask(__name__)
    _app.config.from_object(Config)

    jwt.init_app(_app)
    db.init_app(_app)
    migrate.init_app(_app, db)

    _app.register_blueprint(import_module('app.routes.UserControl').user_control, url_prefix='/api/user')
    _app.register_blueprint(import_module('app.routes.ContentDisplay').content_display, url_prefix='/api')
    _app.register_blueprint(import_module('app.routes.ContentDisplay').channel_management, url_prefix='/api')
    _app.register_blueprint(import_module('app.routes.ContentDisplay').favorite_management, url_prefix='/api')
    _app.register_blueprint(import_module('app.routes.ContentControl').content_control, url_prefix='/api')
    _app.register_blueprint(import_module('app.routes.Admin').admin, url_prefix='/api')

    return _app


app_instance = create_app()


@jwt.token_in_blacklist_loader
def check_blacklisted(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@app_instance.errorhandler(404)
def resource_not_found(e):
    return jsonify({'msg': 'resource not found'}), 404


@app_instance.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'msg': 'method not allowed'}), 405


@app_instance.route('/api')
def hello_world():
    return jsonify({'msg': 'Hello!'})
