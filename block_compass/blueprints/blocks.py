from threading import Thread
from time import sleep
from traceback import print_exc
from datetime import datetime


from web3 import Web3 
from flask import (
    current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)


from ..views import Blocks
from ..utils import SyncThread, MonitorThread
from ..db import (
     get_chains,
     insert_block,
     save_monitor_log,
)


blocks_blueprint = Blueprint('blocks', __name__)
blocks_blueprint.add_url_rule('/blocks', view_func=Blocks.as_view('Blocks'))


@blocks_blueprint.cli.command('sync')
def sync():
    chains = get_chains()
    threads = []
    for chain in chains:
        thread = SyncThread(current_app._get_current_object(), chain, chain["name"])
        thread.start()
        threads.append(thread)
    
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    prettify = lambda cond, text : GREEN + text + ENDC if cond else RED + text + ENDC 

    while True: 
        print('Syncing chains:', *[prettify(thread.is_alive(), f'{thread.name}({thread.last_synced_block})') for thread in threads], end='\r') 
        sleep(1) 


@blocks_blueprint.cli.command('monitor')
def monitor():
    chains = get_chains()
    threads = []
    for chain in chains:
        thread = MonitorThread(current_app._get_current_object(), chain, chain['name'])
        thread.start()
        threads.append(thread)
    
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    prettify = lambda cond, text : GREEN + text + ENDC if cond else RED + text + ENDC 

    while True: 
        print('Monitoring chains: ', *[prettify(thread.is_alive(), f'{thread.name}({thread.latest_monitored_block})') for thread in threads], end='\r') 
        sleep(1) 
    