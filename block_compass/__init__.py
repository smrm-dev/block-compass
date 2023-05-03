import os

import click
from flask import Flask
from flask.cli import FlaskGroup

from .config import env_config

def create_app(config='development'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(env_config[config])

    from .blueprints import blocks_blueprint  
    app.register_blueprint(blocks_blueprint)

    return app

@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the block_compass application."""
