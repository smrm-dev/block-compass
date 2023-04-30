from threading import Thread


from web3 import Web3, EthereumTesterProvider
from flask import (
    current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from ..views import Blocks
from ..db import get_chains, insert_block, init_db

blocks_blueprint = Blueprint('blocks', __name__)
blocks_blueprint.add_url_rule('/blocks', view_func=Blocks.as_view('Blocks'))


@blocks_blueprint.cli.command('sync')
def sync():
    ## TODO: synchronize database
    return

def monitor_chain(app, chain):
    with app.app_context():
        w3 = Web3(Web3.HTTPProvider(chain['rpc']))
        new_block_filter = w3.eth.filter('latest')
        while True:
            new_blocks = new_block_filter.get_new_entries()
            for block_hash in new_blocks:
                while True:
                    try:
                        block = w3.eth.get_block(block_hash)
                        insert_block(block, chain['id'])
                        break
                    except:
                        print('********************', chain['name'], '********************')
                        print_exc()
                        sleep(1)

@blocks_blueprint.cli.command('monitor')
def monitor():
    chains = get_chains()
    for chain in chains:
        thread = Thread(target=monitor_chain, args=(current_app._get_current_object(), chain,)) 
        thread.start()
    print('Monitoring chains: ', [chain['name'] for chain in chains])
    