import sqlalchemy as sa
import click
from flask import current_app, g
from flask.cli import with_appcontext




def get_db():
    if 'db' not in g:
        engine = sa.create_engine(
            r'mssql+pyodbc://computerplan:Comp657plan!@CJVSQL01/inventarisSysteem?driver=ODBC Driver 17 for SQL Server')
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
