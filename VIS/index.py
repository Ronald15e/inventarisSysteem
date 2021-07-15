from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from VIS.db import get_db
from docx import Document
import logging
from docx.enum.style import WD_STYLE_TYPE

bp = Blueprint('index', __name__,)

@bp.route('/')
def index():
    changelog()
    VoorraadCount = count_voorraad()
    return render_template('index.html', user=g.user, VoorraadCount=VoorraadCount)

def write_log(error):
    logging.basicConfig(filename='VIS.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logging.FileHandler('VIS.log')
    logging.exception(error)

def count_voorraad():
    count = get_db().execute(
        ' SELECT Categorie, COUNT(VoorraadID) AS Aantal'
        ' FROM Voorraad voo'
        ' RIGHT JOIN Artikel art on voo.Artikelnummer = art.Artikelnummer'
        ' GROUP BY Categorie '
        ' ORDER BY Aantal DESC, Categorie',
    ).fetchall()
    return count

@bp.route('/changelog')
def changelog():
    doc = Document(r'V:\ICT\VIS\changelog.docx')
    changelog = []
    for para in doc.paragraphs:
        changelog.append(para.text)

    return render_template('changelog.html', changelog=changelog)