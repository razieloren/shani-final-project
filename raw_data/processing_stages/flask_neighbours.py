#!/usr/bin/env python

import sqlite3

from find_neighbours import find_neighbours
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    selected_album = None
    neighbours = []
    if request.method == 'POST':
        gid = request.form.get('albumGid')
        if gid is None:
            raise RuntimeError('No GID supplied in POST')
        selected_album, neighbours = find_neighbours(gid)
    return render_template('index.html', selected_album=selected_album, neighbours=neighbours)
