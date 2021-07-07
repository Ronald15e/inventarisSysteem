from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from inventarisSysteem.auth import login_required
from inventarisSysteem.db import get_db

bp = Blueprint('artikel', __name__ ,url_prefix='/artikel')

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

    return artikel

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
    try:
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
                db = get_db()
                db.execute(
                    'INSERT INTO Artikel (Artikelnaam, Merk, Categorie)'
                    ' VALUES (?, ?, ?)',
                    (artikelnaam, merk, categorie)
                )
                db.commit()
                return redirect(url_for('artikel.index'))

        return render_template('artikel/create.html', categorieen = get_categorie(), merken= get_merk())

    except Exception as e:
        print(e)
        error = 'Er is iets fout gegaan. Je bent teruggestuurd naar de home pagina.'
        flash(error)
        return redirect(url_for('index.index'))

@bp.route('/<int:artikelnummer>/update', methods=('GET', 'POST'))
@login_required
def update(artikelnummer):
    artikel = get_post(artikelnummer)

    try:
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
                flash('Artikel is geüpdatet.', )
                return redirect(url_for('artikel.index'))
        return render_template('artikel/update.html', artikel=artikel)

    except Exception as e:
        print(e)
        error = 'Er is iets fout gegaan. Je bent teruggestuurd naar de home pagina.'
        flash(error)
        return redirect(url_for('index.index'))

@bp.route('/<int:artikelnummer>/delete', methods=('POST',))
@login_required
def delete(artikelnummer):
    db = get_db()
    db.execute('DELETE FROM artikel WHERE artikelnummer = ?', (artikelnummer,))
    db.commit()
    flash('Artikel is verwijderd.')
    return redirect(url_for('artikel.index'))
