from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime

from werkzeug.exceptions import abort

from inventarisSysteem.auth import login_required
from inventarisSysteem.db import get_db

bp = Blueprint('voorraad', __name__)


@bp.route('/')
def index():
    db = get_db()
    voorraad = db.execute(
        'SELECT *'
        ' FROM inventaris'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('voorraad/index.html', posts=voorraad)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        artikelnummer = request.form['artikelnummer']
        naam = request.form['naam']
        categorie = request.form['categorie']
        prijs = request.form['prijs']
        prijs = float(prijs)
        now = datetime.now()
        error = None

        if not artikelnummer:
            error = 'artikelnummer is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO inventaris (artikelnummer, naam, categorie, prijs, created)'
                ' VALUES (?, ?, ?, ? ,?)',
                (artikelnummer, naam, categorie, prijs, now)
            )
            db.commit()
            return redirect(url_for('voorraad.index'))

    return render_template('voorraad/create.html')