import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

# from block_compass.db import get_db

bp = Blueprint('block', __name__, url_prefix='/block')

@bp.route('/timestamp', methods=['GET'])
def timestamp():
    ## TODO: return timestamp of the block
    timestamp = 0
    return str(timestamp)

@bp.cli.command('sync')
def sync():
    ## TODO: synchronize database
    return

@bp.cli.command('monitor')
def monitor():
    ## TODO: monitor blockchain and sync database 
    return