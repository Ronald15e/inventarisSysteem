from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
from werkzeug.exceptions import abort
from inventarisSysteem.auth import login_required
from inventarisSysteem.db import get_db
from flask_wtf import FlaskForm
from wtforms import SelectField


bp = Blueprint('voorraad', __name__, url_prefix='/voorraad')

def get_artikelnummer(Artikelnaam):
    artikelnummer = get_db().execute(
        'SELECT Artikelnummer'
        ' FROM Artikel'
        ' WHERE Artikelnaam = ?',
        (Artikelnaam,)
    ).fetchone()
    return artikelnummer[0]

def get_artikelnaam():
    artikelen = get_db().execute(
        'SELECT Artikelnaam'
        ' FROM Artikel'
        ).fetchall()
    return artikelen

def get_post(VoorraadID):
    VoorraadProduct = get_db().execute(
        ' SELECT VoorraadID, voo.Artikelnummer, Artikelnaam, Merk, Categorie, Prijs, GebruikerID, Gebruikersnaam as GemaaktDoor, '
        ' CAST(CreatieTijd AS smalldatetime) AS CreatieTijd, Opmerking'
        ' FROM Voorraad voo'
        ' JOIN Artikel art ON voo.Artikelnummer = art.Artikelnummer'
        ' JOIN Beheerder beh ON voo.GemaaktDoor = beh.GebruikerID'
        ' WHERE VoorraadID = ?',
        (VoorraadID,)
    ).fetchone()

    if VoorraadID is None:
        abort(404, f"Artikelnummer {VoorraadID} doesn't exist.")

    return VoorraadProduct

def get_personeelnummer(naam, afdeling):
    if naam and afdeling == "":
        print('leeg')
        query = 'SELECT Personeelnummer FROM Medewerker WHERE Naam IS NULL AND Afdeling IS  NULL'
        personeelnummer = get_db().execute(query).fetchone()
    else:
        personeelnummer = get_db().execute(
            ' SELECT Personeelnummer'
            ' FROM Medewerker'
            ' WHERE Naam = ? AND Afdeling = ?;',
            (naam, afdeling)
        ).fetchone()

    return personeelnummer[0]

@bp.route('/')
def index():
    db = get_db()
    voorraad = db.execute(
        'SELECT VoorraadID, voo.Artikelnummer, art.Artikelnaam, Merk, Categorie, Prijs, Gebruikersnaam, CreatieTijd'
        ' FROM Voorraad voo'
        ' JOIN Artikel  art ON voo.Artikelnummer = art.Artikelnummer'
        ' JOIN Beheerder beh ON voo.GemaaktDoor = beh.GebruikerID'
        ' ORDER BY CreatieTijd ASC'
    ).fetchall()
    return render_template('voorraad/index.html', voorraad=voorraad)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    class Artikel():
        db = get_db()
        artikelnummer = db.Column()
        artikelnaam = db.Column(db.Varchar(50))
        merk = db.Column(db.Varchar(25))
        categorie = db.Column(db.Varchar(25))

    class Form(FlaskForm):
        categorie = SelectField('categorie', choices=[('laptop', 'lenovo'), ('telefoon', 'iPhone Xr')])
        artikel = SelectField('artikel', choices=[])

    db = get_db()
    artikelnaam = get_artikelnaam()

    form = Form()
    form.artikel.choices = [(Artikel.categorie, Artikel.artikelnaam )for categorie in Artikel.query.filter_by(categorie='laptop').all()]

    if request.method == 'POST':
        artikelnaam = request.form['Artikelnaam']
        prijs = request.form['Prijs']
        opmerking = request.form['Opmerking']
        error = None

        if prijs != "":
            if ',' in prijs:
                prijs = prijs.replace(',', '.')
                prijs = float(prijs)
            else:
                prijs = float(prijs)
        else:
            None

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO Voorraad (Artikelnummer, Prijs, GemaaktDoor, CreatieTijd, Opmerking)'
                ' VALUES (?, ?, ?, ?, ?)',
                (get_artikelnummer(artikelnaam), prijs, g.user[0], datetime.now(), opmerking)
            )
            db.commit()
            return redirect(url_for('voorraad.index'))

    return render_template('voorraad/create.html', artikelnamen=artikelnaam, form=form)

@bp.route('/<int:VoorraadID>/update', methods=('GET', 'POST'))
@login_required
def update(VoorraadID):
    VoorraadProduct = get_post(VoorraadID)

    if request.method == 'POST':

        prijs = request.form['prijs']
        opmerking = request.form['opmerking']
        error = None

        if prijs != "":
            if ',' in prijs:
                prijs = prijs.replace(',', '.')
                prijs = float(prijs)
            else:
                prijs = float(prijs)
        else:
            None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                ' UPDATE Voorraad SET Prijs  = ?, Opmerking = ?'
                ' WHERE VoorraadID = ?',
                ( prijs, opmerking, VoorraadID)
            )
            db.commit()
            return redirect(url_for('voorraad.index'))
    return render_template('voorraad/update.html', product=VoorraadProduct)

@bp.route('/<int:VoorraadID>/give', methods=('GET', 'POST'))
@login_required
def give(VoorraadID):
    VoorraadProduct = get_post(VoorraadID)

    if request.method == 'POST':
        afdeling = request.form['afdeling']
        naam = request.form['medewerker']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO Productie (ProductieID, Artikelnummer, Prijs, Opmerking, GemaaktDoor, CreatieTijd, UitgifteDoor, UitgifteTijd, Personeelnummer)'
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'
                'DELETE FROM Voorraad WHERE VoorraadID = ?;' ,
                (VoorraadProduct[0], VoorraadProduct[1], VoorraadProduct[5], VoorraadProduct[9], VoorraadProduct[6],
                 VoorraadProduct[8], g.user[0], datetime.now(), get_personeelnummer(naam, afdeling), VoorraadProduct[0])
            )
            db.commit()
            return redirect(url_for('productie.index'))
    return render_template('voorraad/give.html', product= VoorraadProduct)

@bp.route('/<int:VoorraadID>/delete', methods=('POST',))
@login_required
def delete(VoorraadID):
    db = get_db()
    db.execute('DELETE FROM Voorraad WHERE VoorraadID = ?', (VoorraadID,))
    db.commit()
    return redirect(url_for('voorraad.index'))