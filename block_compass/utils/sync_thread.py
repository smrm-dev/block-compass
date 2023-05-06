from threading import Thread
from time import sleep
from traceback import print_exc
from datetime import datetime


from web3 import Web3


from ..db import (
    get_chains,
    get_monitor_logs,
    get_sync_logs,
    insert_block,
    save_monitor_log,
    save_sync_log,
)


class SyncThread(Thread):
    def __init__(self, app, chain, name):
        self.app = app
        self.chain = chain
        self.last_synced_block = None
        Thread.__init__(self, name=name)

    def find_gaps(monitor_logs):
        gaps = []
        for sequent_logs in zip(monitor_logs[:-1], monitor_logs[1:]):
            gaps.append((sequent_logs[0]['toBlock'] + 1, sequent_logs[1]['toBlock'] - sequent_logs[1]['numBlocks'] + 1, sequent_logs[1]['_id']))    
        
        return gaps


    def sync_to_block(chain, start, end):
        w3 = Web3(Web3.HTTPProvider(chain['rpc']))

        for block_number in range(start, end):
            block = w3.eth.get_block(block_number)
            insert_block(block, chain['id'])
            save_sync_log(block_number, chain['id'])


    def sync_chain(app, chain):
        with app.app_context():

            sync_log = get_sync_logs(chain['id'])

            last_synced_block = -1
            if sync_log:
                start = sync_log['toBlock'] + 1
                last_synced_block = sync_log['toBlock']
            else:
                start = 0

            monitor_logs = get_monitor_logs(last_synced_block, chain['id'])

            w3 = Web3(Web3.HTTPProvider(chain['rpc']))

            if monitor_logs == []:
                end = w3.eth.get_block_number()
                sync_to_block(chain, start, end + 1)
            else:
                first_log = monitor_logs[0]
                first_gap_end = first_log['toBlock'] - first_log['numBlocks'] + 1
                gaps = [(start, first_gap_end)]
                gaps += find_gaps(monitor_logs)
                print(chain['name'], gaps)
                for gap in gaps:
                    sync_to_block(chain, start=gap[0], end=gap[1])
                save_sync_log(monitor_logs[-1]['toBlock'], chain['id'])

            print(f'{chain["name"]} synced!')

    def run(self):
        self.__sync_chain(self.app, self.chain)
