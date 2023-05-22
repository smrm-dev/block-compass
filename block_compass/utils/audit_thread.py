from threading import Thread

from flask import current_app
from prompt_toolkit.shortcuts import ProgressBar

from .audit_chunk_thread import AuditChunkThread
from ..db import get_last_synced_block 

class AuditThread(Thread):
    chunks_number = 10
    def __init__(self, app, chain, name):
        self.app = app
        self.chain = chain
        Thread.__init__(self, name=name)

    def __audit_blocks_in_chunks(self, chain_id, last_synced_block):
        chunks_size = int(last_synced_block / self.chunks_number) + 1
        threads = []
        with ProgressBar() as pb:
            for lower_bound in range(0, last_synced_block + 1, chunks_size):
                upper_bound = lower_bound + chunks_size - 1
                upper_bound = upper_bound if upper_bound < last_synced_block else last_synced_block 
                thread = AuditChunkThread(current_app._get_current_object(), chain_id, lower_bound, upper_bound, pb) 
                thread.start()
                threads.append(thread)

            for thread in threads:
                while thread.is_alive():
                    thread.join()

    def __audit_chain(self, chain):
            last_synced_block = get_last_synced_block(chain['id'])
            if last_synced_block == -1:
                return
            
            self.__audit_blocks_in_chunks(chain['id'], last_synced_block)

    def run(self):
        with self.app.app_context():
            self.__audit_chain(self.chain) 