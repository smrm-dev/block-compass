from time import sleep

import click
from flask import (
    current_app,
    Blueprint,
)
from prompt_toolkit.shortcuts import ProgressBar


from ..views import Blocks
from ..utils import SyncThread, MonitorThread, AuditThread
from ..db import (
     get_chains, get_chain
)


blocks_blueprint = Blueprint('blocks', __name__)
blocks_blueprint.add_url_rule('/blocks', view_func=Blocks.as_view('Blocks'))


@blocks_blueprint.cli.command('audit')
@click.argument('chain_id')
def audit(chain_id: int):
    chain = get_chain(int(chain_id)) 
    audit_thread = AuditThread(current_app._get_current_object(), chain, chain["name"])
    audit_thread.start()
    audit_thread.join()

@blocks_blueprint.cli.command('sync')
@click.argument('chain_id')
def sync(chain_id: int):
    chain_id = int(chain_id)
    if chain_id != 0:
        chains = [get_chain(int(chain_id))]
    else:
        chains = get_chains()
    threads = []
    with ProgressBar() as pb:
        for chain in chains:
            thread = SyncThread(current_app._get_current_object(), chain, chain["name"], pb)
            thread.start()
            threads.append(thread)

        for thread in threads:
            while thread.is_alive():
                thread.join()

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
    