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
    productie = get_db().execute(
        ' SELECT ProductieID, pro.Artikelnummer, Artikelnaam, Merk, Categorie, Prijs, Opmerking, behA.Gebruikersnaam as GemaaktDoor, '
        ' CreatieTijd, behB.Gebruikersnaam as UitgifteDoor, UitgifteTijd, pro.Personeelnummer, Naam, Afdeling'
        ' FROM Productie pro '
        ' JOIN Artikel art ON pro.Artikelnummer = art.Artikelnummer'
        ' LEFT JOIN Beheerder behA ON pro.GemaaktDoor = behA.GebruikerID'
        ' LEFT JOIN Beheerder behB ON pro.UitgifteDoor = behB.GebruikerID'
        ' JOIN Medewerker med on pro.Personeelnummer = med.Personeelnummer'
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

def get_post(ProductieID):
    ProductieProduct = get_db().execute(
         ' SELECT ProductieID, pro.Artikelnummer, Artikelnaam, Merk, Categorie, Prijs, Opmerking, behA.Gebruikersnaam as GemaaktDoor, '
         ' CreatieTijd, behB.Gebruikersnaam as UitgifteDoor, UitgifteTijd, pro.Personeelnummer, Naam, Afdeling'
         ' FROM Productie pro '
         ' JOIN Artikel art ON pro.Artikelnummer = art.Artikelnummer'
         ' LEFT JOIN Beheerder behA ON pro.GemaaktDoor = behA.GebruikerID'
         ' LEFT JOIN Beheerder behB ON pro.UitgifteDoor = behB.GebruikerID'
		 ' JOIN Medewerker med on pro.Personeelnummer = med.Personeelnummer'
		 ' WHERE ProductieID = ?',
        (ProductieID,)
    ).fetchone()

    if ProductieID is None:
        abort(404, f"Artikelnummer {ProductieID} doesn't exist.")

    return ProductieProduct


@bp.route('/<int:ProductieID>/update', methods=('GET', 'POST'))
@login_required
def update(ProductieID):
    product = get_post(ProductieID)

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
                ' UPDATE Productie SET Prijs  = ? , Opmerking = ? '
                ' WHERE ProductieID = ? ',
                (prijs, opmerking, ProductieID)
            )
            db.commit()
            return redirect(url_for('productie.index'))
    return render_template('productie/update.html', product=product)

@bp.route('/<int:ProductieID>/')
@login_required
def product(ProductieID):
    product = get_post(ProductieID)
    return render_template('productie/product.html', product=product)


def get_personeelnummer(naam, afdeling):
    if naam and afdeling == "":
        query = 'SELECT Personeelnummer FROM Medewerker WHERE Naam IS NULL AND Afdeling IS  NULL'
        personeelnummer = get_db().execute(query).fetchone()

    else:
        personeelnummer = get_db().execute(
            'SELECT Personeelnummer'
            'FROM Medewerker'
            'WHERE Naam = ? and Afdeling = ?',
            (naam, afdeling)
        ).fetchone()

    return personeelnummer[0]

# @bp.route('/<int:VoorraadID>/give', methods=('GET', 'POST'))
# @login_required
# def give(VoorraadID):
#     VoorraadProduct = get_post(VoorraadID)
#
#     if request.method == 'POST':
#         persoon = request.form['medewerker']
#         afdeling = request.form['afdeling']
#         user = g.user[0]
#         now = datetime.now()
#         error = None
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO Productie (ProductieID, Artikelnummer, Prijs, Opmerking, GemaaktDoor, CreatieTijd, UitgifteDoor, UitgifteTijd, Personeelnummer)'
#                 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'
#                 'DELETE FROM Voorraad WHERE VoorraadID = ?;' ,
#                 (VoorraadProduct[0], VoorraadProduct[1], VoorraadProduct[5], VoorraadProduct[9], VoorraadProduct[6],
#                  VoorraadProduct[8], g.user[0], datetime.now(), get_personeelnummer(persoon, afdeling), VoorraadProduct[0])
#             )
#             db.commit()
#             return redirect(url_for('voorraad.index'))
#     return render_template('voorraad/give.html', product= VoorraadProduct)

@bp.route('/<int:ProductieID>/delete', methods=('POST',))
@login_required
def delete(ProductieID):
    db = get_db()
    db.execute('DELETE FROM Productie WHERE ProductieID = ?', (ProductieID,))
    db.commit()
    return redirect(url_for('voorraad.index'))

@bp.route('/<int:ProductieID>/giveback', methods=('POST', 'GET'))
@login_required
def giveback(ProductieID):
    db = get_db()
    db.execute(' SET IDENTITY_INSERT Voorraad ON;'
               ' INSERT INTO Voorraad (VoorraadID, Artikelnummer, Prijs, GemaaktDoor, CreatieTijd, Opmerking)'
               ' SELECT ProductieID, Artikelnummer, Prijs, GemaaktDoor, CreatieTijd, Opmerking'
               ' FROM Productie '
               ' WHERE ProductieID = ?; '
               ' SET IDENTITY_INSERT Voorraad OFF; '
               ' DELETE FROM Productie WHERE ProductieID = ? ;',
               (ProductieID, ProductieID))
    db.commit()
    return redirect(url_for('voorraad.index'))