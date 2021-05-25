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

def get_post(artikelnummer, check_author=True):
    post = get_db().execute(
        'SELECT *'
        ' FROM inventaris'
        ' WHERE artikelnummer = ?',
        (artikelnummer,)
    ).fetchone()

    if post is None:
        abort(404, f"Artikelnummer {artikelnummer} doesn't exist.")

    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    return post


@bp.route('/<int:artikelnummer>/update', methods=('GET', 'POST'))
@login_required
def update(artikelnummer):
    post = get_post(artikelnummer)

    if request.method == 'POST':
        artikelnummer = request.form['artikelnummer']
        naam = request.form['naam']
        categorie = request.form['categorie']
        prijs = request.form['prijs']
        prijs = float(prijs)
        now = datetime.now()
        error = None

        if not artikelnummer:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE inventaris SET artikelnummer = ? ,naam = ?, categorie = ?, prijs  = ?'
                ' WHERE artikelnummer = ?',
                (artikelnummer, naam, categorie, prijs,artikelnummer)
            )
            db.commit()
            return redirect(url_for('voorraad.index'))
    return render_template('voorraad/update.html', post=post)

@bp.route('/<int:artikelnummer>/delete', methods=('POST',))
@login_required
def delete(artikelnummer):
    get_post(artikelnummer)
    db = get_db()
    db.execute('DELETE FROM inventaris WHERE artikelnummer = ?', (artikelnummer,))
    db.commit()
    return redirect(url_for('voorraad.index'))