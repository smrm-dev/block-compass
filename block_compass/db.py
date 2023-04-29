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

def get_chains():
    result = db.chains.find()
    return result

def get_block_by_timestamp(timestamp, chain_id):
    result = db.blocks.find_one_or_404({'timestamp': {'$lte': timestamp}, 'chainId': chain_id}, projection={'_id' : False}) 
    return result 