from flask import Flask
from app.models import db
from app.extensions import ma
from app.blueprints.members import members_bp


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    #Add extensions to app
    db.init_app(app)
    ma.init_app(app)

    #registering blueprints
    app.register_blueprint(members_bp, url_prefix='/members')


    return app


