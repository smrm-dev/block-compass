from threading import Thread


from web3 import Web3
from flask import current_app


from ..db import (
    get_monitor_logs,
    get_sync_log,
    save_sync_log,
    update_sync_log,
    finalize_sync_log,
)
from .chunk_thread import ChunkThread


class SyncThread(Thread):
    def __init__(self, app, chain, name, pb):
        self.app = app
        self.chain = chain
        self.threads = []
        self.pb = pb
        Thread.__init__(self, name=name)

    def __find_gaps(self, start, monitor_logs, chain):
        if monitor_logs == []:
            w3 = Web3(Web3.HTTPProvider(chain['rpc']))
            end = w3.eth.get_block_number()
            return [(start, end + 1, end - start + 1)]
        else:
            first_log = monitor_logs[0]
            first_gap_end = first_log['toBlock'] - first_log['numBlocks'] + 1

            gaps = []
            if start < first_gap_end - 1:
                gaps += [(start, first_gap_end, first_gap_end - start)]

            for sequent_logs in zip(monitor_logs[:-1], monitor_logs[1:]):
                gap_start = sequent_logs[0]['toBlock'] + 1
                gap_end = sequent_logs[1]['toBlock'] - sequent_logs[1]['numBlocks'] + 1
                gap_length = gap_end - gap_start
                if gap_length == 0:
                    continue
                gaps.append((gap_start, gap_end, gap_end - gap_start))    
        
        return gaps

    def __sync_blocks_in_chunks(self, gaps, chain):
        def split_gap(gap, chunk_free_space):
            split_point = gap[0] + chunk_free_space
            return [(gap[0], split_point, chunk_free_space), (split_point, gap[1], gap[2] - chunk_free_space)] 
        
        to_block = gaps[-1][1] - 1
        num_blocks_to_sync = sum([gap[2] for gap in gaps])

        # TODO: should fetch chain rpcs 
        num_chain_rpcs = 3 
        chain_rpcs = ['1', '2', '3']

        #TODO: manage sync processes with a few number of blocks 
        average_chunk_size = (num_blocks_to_sync // num_chain_rpcs) + 1

        chunks = {api_key: [] for api_key in chain_rpcs}
        for chain_rpc in chain_rpcs:
            chunk_gaps = []
            chunk_size = 0

            last_index = -1 
            for index, gap in enumerate(gaps):
                gap_size = gap[2]

                if gap_size + chunk_size <= average_chunk_size:

                    chunk_gaps.append(gap)
                    chunk_size += gap_size
                    last_index += 1
                    if chunk_size == average_chunk_size:
                        break
                    continue

                (gap_0, gap_1) = split_gap(gap, average_chunk_size - chunk_size) 
                gaps[index] = gap_1
                chunk_gaps.append(gap_0)
                break

            chunks[chain_rpc] = { 'gaps':chunk_gaps, 'chainId': chain['id'] }
            gaps = gaps[last_index + 1:]

        update_sync_log(chain['id'], list(chunks.values()), to_block)
        for chain_rpc in chain_rpcs:
            thread = ChunkThread(current_app._get_current_object(), chain_rpc, chunks[chain_rpc], chain, self.pb) 
            thread.start()
            self.threads.append(thread)
        
        for thread in self.threads:
            while thread.is_alive():
                thread.join()
        
        finalize_sync_log(chain['id'])

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
            if gaps == []:
                print(f'{chain["name"]} has already synced!')
                return

            print(chain['name'], gaps)
            self.__sync_blocks_in_chunks(gaps, chain)

            print(f'{chain["name"]} synced!')

    def run(self):
        self.__sync_chain(self.app, self.chain)
