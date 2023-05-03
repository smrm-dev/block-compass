from threading import Thread
from time import sleep
from traceback import print_exc
from datetime import datetime


from web3 import Web3, EthereumTesterProvider
from flask import (
    current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)


from ..views import Blocks
from ..db import get_chains, insert_block, save_monitor_log, get_monitor_logs, get_sync_logs, save_sync_log 


blocks_blueprint = Blueprint('blocks', __name__)
blocks_blueprint.add_url_rule('/blocks', view_func=Blocks.as_view('Blocks'))

def sync_chain(app, chain):
    with app.app_context():

        sync_log = get_sync_logs(chain['id'])
        monitor_logs = get_monitor_logs(chain['id'])

        w3 = Web3(Web3.HTTPProvider(chain['rpc']))

        if sync_log:
            start = sync_log['toBlock'] + 1
        else:
            start = 0

        if monitor_logs == []:
            end = latest_block = w3.eth.get_block_number
        else:
            first_log = monitor_logs[0]
            end = first_log['toBlock'] - first_log['numBlocks'] + 1
            sync_gaps(monitor_logs)

        sync_to_block(chain, start, end)

        print(f'{chain["name"]} synced!')


@blocks_blueprint.cli.command('sync')
def sync():
    chains = get_chains()
    threads = []
    for chain in chains:
        thread = Thread(target=sync_chain, args=(current_app._get_current_object(), chain,), name=chain['name']) 
        thread.start()
        threads.append(thread)


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
            sleep(chain['blockTime'])


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
    