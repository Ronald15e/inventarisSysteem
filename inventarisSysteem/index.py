from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from inventarisSysteem.db import get_db

bp = Blueprint('index', __name__,)

@bp.route('/')
def index():
    VoorraadCount = count_voorraad()
    return render_template('index.html', user=g.user, VoorraadCount=VoorraadCount)

def count_voorraad():
    count = get_db().execute(
        ' SELECT Categorie, COUNT(VoorraadID)'
        ' FROM Voorraad voo'
        ' JOIN Artikel art on voo.Artikelnummer = art.Artikelnummer'
        ' GROUP BY Categorie ',
    ).fetchall()
    return count