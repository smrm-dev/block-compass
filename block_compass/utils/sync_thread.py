from threading import Thread
from functools import reduce


from web3 import Web3


from ..db import (
    get_monitor_logs,
    get_sync_log,
    insert_block,
    save_sync_log,
)


class SyncThread(Thread):
    def __init__(self, app, chain, name):
        self.app = app
        self.chain = chain
        self.last_synced_block = None
        Thread.__init__(self, name=name)

    def __find_gaps(self, start, monitor_logs, chain):
        if monitor_logs == []:
            w3 = Web3(Web3.HTTPProvider(chain['rpc']))
            end = w3.eth.get_block_number()
            return [(start, end + 1)]
        else:
            first_log = monitor_logs[0]
            first_gap_end = first_log['toBlock'] - first_log['numBlocks'] + 1
            gaps = [(start, first_gap_end)]

            for sequent_logs in zip(monitor_logs[:-1], monitor_logs[1:]):
                gaps.append((sequent_logs[0]['toBlock'] + 1, sequent_logs[1]['toBlock'] - sequent_logs[1]['numBlocks'] + 1))    
        
        return gaps

    def __sync_to_block(self, chain, start, end):
        w3 = Web3(Web3.HTTPProvider(chain['rpc']))

        for block_number in range(start, end):
            block = w3.eth.get_block(block_number)
            insert_block(block, chain['id'])
            save_sync_log(block_number, chain['id'])
            self.last_synced_block = block_number

    def __sync_chain(self, app, chain):

        with app.app_context():

            (finished, sync_log_gaps, last_synced_block) = get_sync_log(chain['id'])

            start = last_synced_block + 1

            monitor_logs = get_monitor_logs(last_synced_block, chain['id'])

            w3 = Web3(Web3.HTTPProvider(chain['rpc']))

            gaps = []
            if not finished:
                gaps += sync_log_gaps

            gaps += self.__find_gaps(start, monitor_logs, chain)

            self.__sync_blocks_in_chunks(gaps, chain)

            print(f'{chain["name"]} synced!')

    def run(self):
        self.__sync_chain(self.app, self.chain)
