import sys

from flask import Flask
from argon2 import PasswordHasher

from importlib import import_module

sys.path.append('../')
Config = import_module('app.KoinuConfig').DebugConfig
from app.Models import *
sys.path.pop()

argon2 = PasswordHasher()


def create_app():
    _app = Flask('114514')
    _app.config.from_object(Config)
    db.init_app(_app)
    return _app


app = create_app()
app.app_context().push()
