from threading import Thread

from flask import current_app
from prompt_toolkit.shortcuts import ProgressBar

from ..db import get_last_synced_block, get_blocks_by_number, update_audit_result, update_sync_log

class AuditThread(Thread):
    chunk_size = int(100e3)
    def __init__(self, app, chain, name):
        self.app = app
        self.chain = chain
        Thread.__init__(self, name=name)

    def __audit_chunk(self, chain_id, lower_bound, upper_bound):
        blocks_to_audit = [block['number'] for block in get_blocks_by_number(chain_id, lower_bound, upper_bound)]
        expected_block_number = lower_bound
        last_audited_block = -1
        gaps = []
        for current_block_number in blocks_to_audit:
            if current_block_number != expected_block_number:
                gaps.append((expected_block_number, current_block_number))
                expected_block_number = current_block_number + 1
            else:
                expected_block_number += 1
            last_audited_block = current_block_number
        
        if last_audited_block != upper_bound:
            gaps.append((expected_block_number, upper_bound + 1))
        
        return gaps

    def __audit_blocks_in_chunks(self, chain_id, last_synced_block):
        def merge_or_return_gaps(gap_0, gap_1):
            if gap_0[1] == gap_1[0]:
                return [(gap_0[0], gap_1[1])]
            return [gap_0, gap_1] 

        with ProgressBar() as pb:
            gaps = []
            for lower_bound in pb(range(0, last_synced_block + 1, self.chunk_size)):
                upper_bound = lower_bound + self.chunk_size - 1
                upper_bound = upper_bound if upper_bound < last_synced_block else last_synced_block 
                chunk_gaps = self.__audit_chunk(chain_id, lower_bound, upper_bound)
                if chunk_gaps:
                    if gaps:
                        gap_0 = gaps[-1]
                        gap_1 = chunk_gaps[0]
                        gaps = gaps[:-1] + merge_or_return_gaps(gap_0, gap_1) + chunk_gaps[1:]
                    else:
                        gaps += chunk_gaps
                    update_audit_result(chain_id, gaps)
            return gaps
            
    def __audit_chain(self, chain):
            chain_id = chain['id']
            last_synced_block = get_last_synced_block(chain_id)
            if last_synced_block == -1:
                print('NO_BLOCK_FOUND')
                return
            
            #TODO: should check for previous audit
            
            gaps = self.__audit_blocks_in_chunks(chain_id, last_synced_block)

            update_sync_log(chain_id, [{'gaps': gaps, 'chainId': chain_id}], last_synced_block)

            if gaps:
                print(gaps)
                print('Missing Blocks')
                pass
            else:
                print('All Right')

    def run(self):
        with self.app.app_context():
            self.__audit_chain(self.chain) 