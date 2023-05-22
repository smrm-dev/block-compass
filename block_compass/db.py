from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo, DESCENDING, ASCENDING

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


def init_db(app):
    with app.app_context():
        db.chains.create_index([('id', ASCENDING)], unique=True)
        db.blocks.create_index([('timestamp', DESCENDING), ('number', DESCENDING), ('chainId', ASCENDING)])
        db.monitorLogs.create_index([('toBlock', ASCENDING), ('chainId', ASCENDING)])

def delete_chunk_log(chunk_id):
    db.chunkLogs.delete_one({ '_id': chunk_id })

def update_chunk_log(chunk_id):
    chunk_log = db.chunkLogs.find_one( filter= { '_id': chunk_id })

    chunk_gaps = chunk_log['gaps']
    current_gap = chunk_gaps[0]
    current_gap = [current_gap[0] + 1, current_gap[1], current_gap[2] - 1]
    if current_gap[2] == 0:
        chunk_gaps = chunk_gaps[1:]
    else:
        chunk_gaps[0] = current_gap
    
    db.chunkLogs.update_one( 
        filter= { '_id': chunk_id },
        update= { '$set': { 'gaps': chunk_gaps } }
    )

def finalize_sync_log(chain_id):
    db.syncLogs.update_one(
        filter= { 'chainId': chain_id },
        update= { '$set': { 'finished': True } }
    )

def update_sync_log(chain_id, chunks, to_block):
    db.syncLogs.update_one(
        filter= { 'chainId': chain_id },
        update= { '$set': { 'toBlock': to_block, 'finished': False } },
        upsert= True
    )

    db.chunkLogs.delete_many({'chainId': chain_id})
    db.chunkLogs.insert_many(chunks)

def get_sync_log(chain_id):
    result = db.syncLogs.find_one({'chainId': chain_id})
    if result == None:
        return (True, [], -1)
    chunks = db.chunkLogs.find({'chainId': chain_id})
    gaps = []
    for chunk in chunks:
        gaps += chunk['gaps']
    return result['finished'], gaps, result["toBlock"]

def get_last_synced_block(chain_id):
    result = db.syncLogs.find_one({'chainId': chain_id})
    if result == None:
        return -1
    return result["toBlock"]


def get_monitor_logs(block_number, chain_id):
    result = db.monitorLogs.find({'chainId': chain_id, 'toBlock': {'$gt': block_number}})
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

def get_chain(chain_id):
    chain = db.chains.find_one_or_404({'id': chain_id})
    return chain

def get_chains():
    result = db.chains.find()
    return list(result)

def init_chains(chains):
    db.chains.delete_many({})
    db.chains.insert_many(chains)

def get_genesis_block_timestamp(chain_id):
    return db.blocks.find_one({'chainId': chain_id, 'number': 0})['timestamp']

def get_block_number_by_timestamp(timestamp, chain_id):
    chain = db.chains.find_one_or_404({'id': chain_id})
    result = db.blocks.find_one_or_404({'timestamp': {'$lte': timestamp}, 'chainId': chain_id}, projection={'_id' : False}) 
    if  timestamp - result['timestamp'] > chain['blockTime']:
        return 'NOT_SYNCED' 
    return result['number']