import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from ..views import Blocks

blocks_blueprint = Blueprint('blocks', __name__)
blocks_blueprint.add_url_rule('/blocks', view_func=Blocks.as_view('Blocks'))


@blocks_blueprint.cli.command('sync')
def sync():
    ## TODO: synchronize database
    return

@blocks_blueprint.cli.command('monitor')
def monitor():
    ## TODO: monitor blockchain and sync database 
    return