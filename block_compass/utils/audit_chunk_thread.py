from threading import Thread

class AuditChunkThread(Thread):
    def __init__(self, app, chain_id, lower_bound, upper_bound, pb):
        self.app = app
        self.chain_id = chain_id
        self.lower_bound = lower_bound 
        self.upper_bound = upper_bound
        self.pb = pb
        Thread.__init__(self)
