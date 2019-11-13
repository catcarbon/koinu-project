import os

class KoinuConfig(object):
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = 'random-string-here-please...'
    FLASK_SECRET = SECRET_KEY
    DB_HOST = 'database'
    #####
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

class ProductionConfig(KoinuConfig):
    DB_HOST = 'production.database' # make linter happy...

class DebugConfig(KoinuConfig):
    DEBUG = True
    DEVELOPMENT = True

DefaultConfig = ProductionConfig()
ActiveConfig = DebugConfig()
