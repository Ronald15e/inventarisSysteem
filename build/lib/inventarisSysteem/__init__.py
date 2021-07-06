import os
from flask import Flask
# set FLASK_APP=inventarisSysteem
# set FLASK_ENV=development
# flask run

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'inventarisSysteem.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import voorraad
    app.register_blueprint(voorraad.bp)
    # app.add_url_rule('/', endpoint='index')

    from . import artikel
    app.register_blueprint(artikel.bp)

    from . import productie
    app.register_blueprint(productie.bp)

    from . import index
    app.register_blueprint(index.bp)

    return app

