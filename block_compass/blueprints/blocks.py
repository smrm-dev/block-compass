from threading import Thread
from time import sleep
from traceback import print_exc
from datetime import datetime


from web3 import Web3, EthereumTesterProvider
from flask import (
    current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)


from ..views import Blocks
from ..db import get_chains, insert_block, save_monitor_log 

blocks_blueprint = Blueprint('blocks', __name__)
blocks_blueprint.add_url_rule('/blocks', view_func=Blocks.as_view('Blocks'))


@blocks_blueprint.cli.command('sync')
def sync():
    ## TODO: synchronize database
    return

def monitor_chain(app, chain):
    with app.app_context():
        start_time = datetime.now()
        w3 = Web3(Web3.HTTPProvider(chain['rpc']))
        new_block_filter = w3.eth.filter('latest')
        while True:
            new_blocks = new_block_filter.get_new_entries()
            for block_hash in new_blocks:
                while True:
                    try:
                        block = w3.eth.get_block(block_hash)
                        insert_block(block, chain['id'])
                        save_monitor_log(start_time, block['number'], chain['id'])
                        break
                    except:
                        print('********************', chain['name'], '********************')
                        print_exc()
                        sleep(1)

@blocks_blueprint.cli.command('monitor')
def monitor():
    chains = get_chains()
    threads = []
    for chain in chains:
        thread = Thread(target=monitor_chain, args=(current_app._get_current_object(), chain,), name=chain['name']) 
        thread.start()
        threads.append(thread)
    
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    prettify = lambda cond, text : GREEN + text + ENDC if cond else RED + text + ENDC 

    while True: 
        print('Monitoring chains: ', *[prettify(thread.is_alive(), thread.name) for thread in threads], end='\r') 
        sleep(1) 
    