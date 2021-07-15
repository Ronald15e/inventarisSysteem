import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from wtforms import SelectField
from flask_wtf import FlaskForm
# set FLASK_APP=VIS
# set FLASK_ENV=development
# flask run

def create_app():
    app = Flask('VIS')
    app.config.from_mapping(
        SECRET_KEY='dev',
        FLASK_APP='VIS',
        FLASK_ENV='development',
        SQLALCHEMY_DATABASE_URI='mssql+pyodbc://computerplan:Comp657plan!@192.168.0.152/VIS_copy',
        SQLALCHEMY_TRACK_MODIFICATION=False,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import voorraad
    app.register_blueprint(voorraad.bp)

    from . import artikel
    app.register_blueprint(artikel.bp)

    from . import productie
    app.register_blueprint(productie.bp)

    from . import index
    app.register_blueprint(index.bp)

    return app

# class Artikel(db.Model):
#     artikelnummer = db.Column(db.Integer, primary_key=True)
#     artikelnaam = db.Column(db.String(50))
#     merk = db.Column(db.String(25))
#     categorie = db.Column(db.String(25))
#
# class Form(FlaskForm):
#     categorie = SelectField('categorie', choices=[('laptop', 'lenovo'), ('telefoon', 'iPhone Xr')])
#     artikel = SelectField('artikel', choices=[])