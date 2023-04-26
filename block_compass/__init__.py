import os

import click
from flask import Flask
from flask.cli import FlaskGroup


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    from . import block
    app.register_blueprint(block.bp)

    return app

@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the block_compass application."""
