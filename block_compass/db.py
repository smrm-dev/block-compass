from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo

def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:

        db = g._database = PyMongo(current_app).db
       
    return db

# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def init_db():
    return


def save_sync_log(block_number, chain_id):
    db.syncLogs.update_one(
        filter= {'chainId': chain_id},
        update= { '$set': { 'toBlock': block_number } },
        upsert= True
    )


def get_sync_logs(chain_id):
    result = db.syncLogs.find_one({'chainId': chain_id})
    return result


def get_monitor_logs(chain_id):
    result = db.monitorLogs.find({'chainId': chain_id})
    return list(result)


def save_monitor_log(start_time, block_number, chain_id):
    db.monitorLogs.update_one(
        filter= { 'startTime': start_time },
        update= { '$set': { 'toBlock': block_number, 'chainId': chain_id }, '$inc': {'numBlocks': 1} },
        upsert= True
    )


def insert_block(block, chain_id):
    db.blocks.insert_one({
        'number': block['number'],
        'timestamp': block['timestamp'],
        'chainId': chain_id,
    })


def get_chains():
    result = db.chains.find()
    return list(result)


def get_block_by_timestamp(timestamp, chain_id):
    result = db.blocks.find_one_or_404({'timestamp': {'$lte': timestamp}, 'chainId': chain_id}, projection={'_id' : False}) 
    return result