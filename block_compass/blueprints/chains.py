from flask import (
    current_app,
    Blueprint,
)


from ..views import Chains 
from ..db import (
     get_chains,
)


chains_blueprint = Blueprint('chains', __name__)
chains_blueprint.add_url_rule('/chains', view_func=Chains.as_view('Chains'))