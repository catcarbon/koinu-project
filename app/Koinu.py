from flask import Flask, render_template, request
from importlib import import_module

Config = import_module('KoinuConfig').ActiveConfig
Page = import_module('KoinuPage').IndexPage
# UserControl = import_module('modules.UserControl')

app = Flask(__name__)

@app.route('/')
def hello_world(user=None):
  return render_template('index.jinja', user=user, _env=Config, _page=Page)

if __name__ == "__main__":
  app.run(host='127.0.0.1', debug=Config.DEBUG)
