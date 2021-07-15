from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from VIS.auth import login_required
from VIS.db import get_db
from VIS.voorraad import check_prijs, get_afdelingen, get_personeelnummer, get_medewerkers

bp = Blueprint('productie', __name__, url_prefix='/productie')

def get_post(ProductieID):
    ProductieProduct = get_db().execute(
         ' SELECT ProductieID, pro.Artikelnummer, Artikelnaam, Merk, Categorie, Prijs, Opmerking, behA.Gebruikersnaam as GemaaktDoor, '
         ' CAST(CreatieTijd AS smalldatetime) AS CreatieTijd, behB.Gebruikersnaam as UitgifteDoor, CAST(UitgifteTijd AS smalldatetime) AS UitgifteTijd, pro.Personeelnummer, Naam, Afdeling'
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

@bp.route('/')
def index():
    try:
        productie = get_db().execute(
            ' SELECT ProductieID, pro.Artikelnummer, Artikelnaam, Merk, Categorie, Prijs, Opmerking, behA.Gebruikersnaam as GemaaktDoor, '
            ' CAST(CreatieTijd AS smalldatetime) AS CreatieTijd, behB.Gebruikersnaam as UitgifteDoor, CAST(UitgifteTijd AS smalldatetime) AS UitgifteTijd, pro.Personeelnummer, Naam, Afdeling'
            ' FROM Productie pro '
            ' JOIN Artikel art ON pro.Artikelnummer = art.Artikelnummer'
            ' LEFT JOIN Beheerder behA ON pro.GemaaktDoor = behA.GebruikerID'
            ' LEFT JOIN Beheerder behB ON pro.UitgifteDoor = behB.GebruikerID'
            ' JOIN Medewerker med on pro.Personeelnummer = med.Personeelnummer'
        ).fetchall()
        return render_template('productie/index.html', productie=productie)

    except Exception as e:
        print(e)
        error = 'Er is iets fout gegaan. Je bent teruggestuurd naar de home pagina.'
        flash(error)
        return redirect(url_for('index.index'))

@bp.route('/<int:ProductieID>/update', methods=('GET', 'POST'))
@login_required
def update(ProductieID):
    product = get_post(ProductieID)
    try:
        if request.method == 'POST':
            prijs = request.form['prijs']
            opmerking = request.form['opmerking']
            naam = request.form['medewerker']
            afdeling = request.form['afdeling']
            error = None

            if prijs.isdecimal() == False:
                prijs, error = check_prijs(prijs)

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    ' UPDATE Productie SET Prijs  = ? , Opmerking = ? , Personeelnummer = ? '
                    ' WHERE ProductieID = ? ',
                    (prijs, opmerking, get_personeelnummer(naam, afdeling),ProductieID)
                )
                db.commit()
                flash('Item is geüpdatet.')
                return redirect(url_for('productie.index'))
        return render_template('productie/update.html', product=product, afdelingen=get_afdelingen(), medewerkers=get_medewerkers())

    except Exception as e:
        print(e)
        error = 'Er is iets fout gegaan. Je bent teruggestuurd naar de home pagina.'
        flash(error)
        return redirect(url_for('index.index'))

@bp.route('/<int:ProductieID>/')
@login_required
def product(ProductieID):
    product = get_post(ProductieID)
    return render_template('productie/product.html', product=product)

@bp.route('/<int:ProductieID>/delete', methods=('POST',))
@login_required
def delete(ProductieID):
    db = get_db()
    print('')
    db.execute(' INSERT INTO HProductie'
               ' SELECT * FROM Productie'
               ' WHERE ProductieID = ?;'
               ' DELETE FROM Productie WHERE ProductieID = ?;', (ProductieID, ProductieID))
    db.commit()
    flash('Item is verwijderd en uit productie')
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
    flash('Item is uit productie gehaald en terug naar de voorraad verplaatst.')
    return redirect(url_for('voorraad.index'))