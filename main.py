from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify

from webscrapping.webscrapping import MangaScrapping

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

    for entrada in manganato_updates:
        date = MangaScrapping().get_date_from_string(manganato_updates[entrada]['updated'])
        manganato_updates[entrada]['updated'] = MangaScrapping().get_string_from_timestamp(date)

    return flask.render_template('index.html', mangas=manganato_updates)


if __name__ == '__main__':
    try:
        MangaScrapping().routine_initialization()
    except Exception as e:
        print(f'Error: {e}')

    app.run(host='0.0.0.0', debug=True)