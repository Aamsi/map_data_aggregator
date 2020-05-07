from flask import render_template
from app import app_map


@app_map.route('/')
@app_map.route('/index')
def index():
    return render_template('conflict.html', title='Conflicts')