from flask_sqlalchemy import SQLAlchemy
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        # params = urllib.parse.quote_plus(
        # "DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.0.152;DATABASE=VIS_copy;UID=computerplan;PWD=Comp657plan!")
        # engine = sa.create_engine(sa_url="mssql+pyodbc:///?odbc_connect=%s" % params, self=None, engine_opts=None)
        engine = SQLAlchemy.create_engine(sa_url=
            r'mssql+pyodbc://computerplan:Comp657plan!@192.168.0.152/VIS?driver=ODBC Driver 17 for SQL Server', engine_opts={}, self=None)
        g.db = engine.raw_connection()

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read().decode('utf8'))

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')