from threading import Thread
from time import sleep
from traceback import print_exc
from datetime import datetime


from web3 import Web3, EthereumTesterProvider
from flask import (
    current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)


from ..views import Blocks
from ..db import (
     get_chains, get_monitor_logs, get_sync_logs,
     insert_block, save_monitor_log, save_sync_log,
     delete_monitor_log,
)


blocks_blueprint = Blueprint('blocks', __name__)
blocks_blueprint.add_url_rule('/blocks', view_func=Blocks.as_view('Blocks'))


def find_gaps(monitor_logs):
    gaps = []
    for sequent_logs in zip(monitor_logs[:-1], monitor_logs[1:]):
        gaps.append((sequent_logs[0]['toBlock'] + 1, sequent_logs[1]['toBlock'] - sequent_logs[1]['numBlocks'] + 1, sequent_logs[1]['_id']))    
    
    return gaps


def sync_to_block(chain, start, end, log_id = None):
    w3 = Web3(Web3.HTTPProvider(chain['rpc']))

    for block_number in range(start, end):
        block = w3.eth.get_block(block_number)
        insert_block(block, chain['id'])
        save_sync_log(block_number, chain['id'])

    if log_id:
        delete_monitor_log(log_id)


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
            end = w3.eth.get_block_number()
            sync_to_block(chain, start, end + 1)
        else:
            first_log = monitor_logs[0]
            end = first_log['toBlock'] - first_log['numBlocks'] + 1
            gaps = [(start, end, first_log['_id'])]
            gaps += find_gaps(monitor_logs)
            print(chain['name'], gaps)
            for gap in gaps:
                sync_to_block(chain, start=gap[0], end=gap[1], log_id=gap[2])

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
    