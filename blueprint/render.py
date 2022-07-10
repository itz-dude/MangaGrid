# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import json

from flask import Blueprint, render_template

from webscrapping.webscrapping import MangaScrapping


# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
render = Blueprint('render', __name__)

@render.route('/')
def index():
    with open('webscrapping/results/manganato_updates.json') as json_file:
        manganato_updates = json.load(json_file)

    for entrada in manganato_updates:
        date = MangaScrapping().get_date_from_string(manganato_updates[entrada]['updated'])
        manganato_updates[entrada]['updated'] = MangaScrapping().get_string_from_timestamp(date)

    return render_template('index.html', mangas=manganato_updates)