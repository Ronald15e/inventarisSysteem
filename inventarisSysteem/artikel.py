from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
from werkzeug.exceptions import abort

from inventarisSysteem.auth import login_required
from inventarisSysteem.db import get_db

bp = Blueprint('artikel', __name__ ,url_prefix='/artikel')

@bp.route('/')
def index():
    db = get_db()
    artikelen = db.execute(
        'SELECT *'
        ' FROM Artikel;'
    ).fetchall()
    return render_template('artikel/index.html', artikelen=artikelen)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    merk = get_merk()
    categorie = get_categorie()
    if request.method == 'POST':
        artikelnaam = request.form['artikelnaam']
        merk = request.form['merk']
        categorie = request.form['categorie']
        error = None

        if not artikelnaam:
            error = 'Artikelnaam is verplicht!.'

        if error is not None:
            flash(error)

        else:
            try:
                db = get_db()
                db.execute(
                    'INSERT INTO Artikel (Artikelnaam, Merk, Categorie)'
                    ' VALUES (?, ?, ?)',
                    (artikelnaam, merk, categorie)
                )
                db.commit()
                return redirect(url_for('artikel.index'))
            except Exception as e:
                e

    return render_template('artikel/create.html', categorieen = categorie, merken= merk)

def get_categorie():
    categorie = get_db().execute(
        'SELECT DISTINCT categorie'
        ' FROM artikel'
        ).fetchall()
    return categorie

def get_merk():
    merk = get_db().execute(
        'SELECT DISTINCT merk'
        ' FROM artikel'
        ).fetchall()
    return merk

def get_post(artikelnummer, check_author=True):
    artikel = get_db().execute(
        'SELECT *'
        ' FROM artikel'
        ' WHERE artikelnummer = ?',
        (artikelnummer,)
    ).fetchone()

    if artikel is None:
        abort(404, f"Artikelnummer {artikelnummer} doesn't exist. Pech")

    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    return artikel


@bp.route('/<int:artikelnummer>/update', methods=('GET', 'POST'))
@login_required
def update(artikelnummer):
    artikel = get_post(artikelnummer)

    if request.method == 'POST':
        artikelnaam = request.form['artikelnaam']
        merk = request.form['merk']
        categorie = request.form['categorie']
        error = None
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE Artikel SET Artikelnaam = ?, Merk = ?, Categorie  = ?'
                ' WHERE Artikelnummer = ?',
                (artikelnaam, merk, categorie, artikelnummer)
            )
            db.commit()
            return redirect(url_for('artikel.index'))
    return render_template('artikel/update.html', artikel=artikel)

@bp.route('/<int:artikelnummer>/delete', methods=('POST',))
@login_required
def delete(artikelnummer):
    # get_post(artikelnummer)
    db = get_db()
    db.execute('DELETE FROM artikel WHERE artikelnummer = ?', (artikelnummer,))
    db.commit()
    return redirect(url_for('artikel.index'))