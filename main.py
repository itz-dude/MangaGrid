from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify

import flask
import json
import os
import sys


# starting app
from extensions import db, return_flask_app

app = return_flask_app()

db.init_app(app)

app.config['JSON_AS_ASCII'] = False
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    with open('webscrapping/results/manganato_updates.json') as json_file:
        manganato_updates = json.load(json_file)

    return flask.render_template('index.html', mangas=manganato_updates)


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='192.168.1.10', debug=True)