from threading import Thread

from web3 import Web3

from ..db import (
    insert_block,
    update_chunk_log,
)

class ChunkThread(Thread):
    def __init__(self, app, rpc, chunk, chain):
        self.app = app
        self.rpc = rpc
        self.chunk = chunk
        self.chain = chain
        Thread.__init__(self)

    def __sync_to_block(self, w3, chain_id, chunk_id, start, end):
        for block_number in range(start, end):
            block = w3.eth.get_block(block_number)
            insert_block(block, chain_id)
            update_chunk_log(chunk_id)
    
    def __sync_chunk(self, rpc, chunk, chain):
        w3 = Web3(Web3.HTTPProvider(rpc))
        for gap in chunk['gaps']:
            self.__sync_to_block(w3, chain['id'], chunk['_id'], start=gap[0], end=gap[1])
        
        #TODO: remove chunk log

    def run(self):
        with self.app.app_context():
            self.__sync_chunk(self.rpc, self.chunk, self.chain)