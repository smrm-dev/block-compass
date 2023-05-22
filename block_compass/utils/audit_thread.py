from threading import Thread

class AuditThread(Thread):
    def __init__(self, app, chain, name):
        self.app = app
        self.chain = chain
        Thread.__init__(self, name=name)
