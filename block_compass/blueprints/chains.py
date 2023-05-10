from json import load

from flask import (
    current_app,
    Blueprint,
)


from ..views import Chains 
from ..db import (
     get_chains,
     init_chains,
)
from ..static.chains import chains


chains_blueprint = Blueprint('chains', __name__)
chains_blueprint.add_url_rule('/chains', view_func=Chains.as_view('Chains'))


@chains_blueprint.cli.command('init')
def init():
    init_chains(chains)