from threading import Thread
from time import sleep
from traceback import print_exc
from datetime import datetime


from web3 import Web3 


from ..db import (
    insert_block,
    save_monitor_log,
)


class MonitorThread(Thread):
    def __init__(self, app, chain, name):
        self.app = app
        self.chain = chain
        self.latest_monitored_block = None
        Thread.__init__(self, name=name)
    
    def __monitor_chain(self, app, chain):
        with app.app_context():
            start_time = datetime.now()
            w3 = Web3(Web3.HTTPProvider(chain['rpcs'][0]))
            
            latest_block = w3.eth.get_block_number()
            latest_monitored_block = latest_block - 1
            while True:
                new_blocks = [block_number for block_number in range(latest_monitored_block + 1, latest_block + 1)]
                for block_number in new_blocks:
                    while True:
                        try:
                            block = w3.eth.get_block(block_number)
                            insert_block(block, chain['id'])
                            save_monitor_log(start_time, block['number'], chain['id'])
                            latest_monitored_block = block['number']
                            self.latest_monitored_block = latest_monitored_block
                            break
                        except:
                            print('********************', chain['name'], '********************')
                            print_exc()
                            sleep(1)
                sleep(chain['blockTime'])
                latest_block = w3.eth.get_block_number()

    def run(self):
        self.__monitor_chain(self.app, self.chain)