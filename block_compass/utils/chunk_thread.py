from threading import Thread

from web3 import Web3


class ChunkThread(Thread):
    def __init__(self, app, rpc, chunk, chain):
        self.app = app
        self.rpc = rpc
        self.chunk = chunk
        self.chain = chain
        Thread.__init__(self)

    def __sync_to_block(self, w3, chain_id, chunk_id, start, end):
        for block_number in range(start, end):
            pass
    
    def __sync_chunk(self, rpc, chunk, chain):
        #TODO: implement
        pass

    def run(self):
        with self.app.app_context():
            self.__sync_chunk(self.rpc, self.chunk, self.chain)