import hashlib
import json


def hash_256(string):
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    
    block_hash = block.__dict__.copy()
    block_hash['transactions'] = [tx.__dict__.copy() for tx in block_hash['transactions']]
    return hash_256(json.dumps(block_hash, sort_keys=True).encode())