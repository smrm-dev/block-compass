from threading import Thread

from ..db import get_blocks_by_number

class AuditChunkThread(Thread):
    def __init__(self, app, chain_id, lower_bound, upper_bound, pb):
        self.app = app
        self.chain_id = chain_id
        self.lower_bound = lower_bound 
        self.upper_bound = upper_bound
        self.pb = pb
        self.gaps = []
        Thread.__init__(self)

    def __audit_chunk(self, chain_id, lower_bound, upper_bound):
        blocks_to_audit = get_blocks_by_number(chain_id, lower_bound, upper_bound)
        expected_block_number = lower_bound
        last_audited_block = -1
        for block in blocks_to_audit:
            current_block_number = block['number']
            if current_block_number != expected_block_number:
                self.gaps.append((expected_block_number, current_block_number))
                expected_block_number = current_block_number + 1
            else:
                expected_block_number += 1
            last_audited_block = current_block_number 
        
        if last_audited_block != upper_bound:
            self.gaps.append((expected_block_number, upper_bound + 1))
            

    def run(self):
        with self.app.app_context():
            self.__audit_chunk(self.chain_id, self.lower_bound, self.upper_bound)

