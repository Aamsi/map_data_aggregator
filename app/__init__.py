from flask import Flask

app_map = Flask(__name__)

from app import routes, settings, fetch, mapping