from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
from werkzeug.exceptions import abort

from inventarisSysteem.auth import login_required
from inventarisSysteem.db import get_db

bp = Blueprint('productie', __name__, url_prefix='/productie')

@bp.route('/')
def index():
    db = get_db()
    productie = db.execute(
        'SELECT *'
        ' FROM Productie pro'
        ' JOIN Artikel art ON pro.Artikelnummer = art.Artikelnummer'
        ' JOIN Beheerder beh ON pro.GemaaktDoor = beh.GebruikerID'
    ).fetchall()
    return render_template('productie/index.html', productie=productie)

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
        ' SELECT VoorraadID, voo.Artikelnummer, Artikelnaam, Merk, Categorie, Prijs, GebruikerID, Gebruikersnaam, CreatieTijd, Opmerking'
        ' FROM Voorraad voo'
        ' JOIN Artikel art ON voo.Artikelnummer = art.Artikelnummer'
        ' JOIN Beheerder beh ON voo.GemaaktDoor = beh.GebruikerID'
        ' WHERE VoorraadID = ?',
        (VoorraadID,)
    ).fetchone()

    if VoorraadID is None:
        abort(404, f"Artikelnummer {VoorraadID} doesn't exist.")

    return VoorraadProduct


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    artikelnaam = get_artikelnaam()

    if request.method == 'POST':
        artikelnaam = request.form['Artikelnaam']
        prijs = request.form['Prijs']
        prijs = float(prijs)
        opmerking = request.form['Opmerking']
        user = g.user[0]
        now = datetime.now()

        error = None

        if not artikelnaam:
            error = 'artikelnaam is required.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO Voorraad (Artikelnummer, Prijs, GemaaktDoor, CreatieTijd, Opmerking)'
                ' VALUES (?, ?, ?, ?, ?)',
                (get_artikelnummer(artikelnaam), prijs, user, now, opmerking)
            )
            db.commit()
            return redirect(url_for('voorraad.index'))

    return render_template('voorraad/create.html', artikelnamen=artikelnaam)

@bp.route('/<int:VoorraadID>/update', methods=('GET', 'POST'))
@login_required
def update(VoorraadID):
    VoorraadProduct = get_post(VoorraadID)

    if request.method == 'POST':
        naam = request.form['naam']
        categorie = request.form['categorie']
        prijs = request.form['prijs']
        prijs = float(prijs)
        now = datetime.now()
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE Voorraad SET naam = ?, categorie = ?, prijs  = ?'
                ' WHERE artikelnummer = ?',
                (naam, categorie, prijs, VoorraadID)
            )
            db.commit()
            return redirect(url_for('voorraad.index'))
    return render_template('voorraad/update.html', product=VoorraadProduct)

def get_personeelnummer(naam, afdeling):
    # if naam or afdeling == None:
    query = 'SELECT Personeelnummer FROM Medewerker WHERE Naam IS NULL AND Afdeling IS  NULL'
    personeelnummer = get_db().execute(query
            # 'SELECT Personeelnummer '
            # 'FROM Medewerker'
            # 'WHERE Naam IS NULL AND Afdeling IS  NULL'
        ).fetchone()
    # else:
    #     personeelnummer = get_db().execute(
    #         'SELECT Personeelnummer'
    #         'FROM Medewerker'
    #         'WHERE Naam = ? and Afdeling = ?'
    #         (naam, afdeling)
    #     ).fetchone()
    print(personeelnummer[0])
    return personeelnummer[0]

@bp.route('/<int:VoorraadID>/give', methods=('GET', 'POST'))
@login_required
def give(VoorraadID):
    VoorraadProduct = get_post(VoorraadID)

    if request.method == 'POST':
        persoon = request.form['medewerker']
        afdeling = request.form['afdeling']
        user = g.user[0]
        now = datetime.now()
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
                 VoorraadProduct[8], g.user[0], datetime.now(), get_personeelnummer(persoon, afdeling), VoorraadProduct[0])
            )
            db.commit()
            return redirect(url_for('voorraad.index'))
    return render_template('voorraad/give.html', product= VoorraadProduct)

@bp.route('/<int:VoorraadID>/delete', methods=('POST',))
@login_required
def delete(VoorraadID):
    db = get_db()
    db.execute('DELETE FROM Voorraad WHERE VoorraadID = ?', (VoorraadID,))
    db.commit()
    return redirect(url_for('voorraad.index'))