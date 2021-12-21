"""
Blockchain (stub).
NB: Feel free to extend or modify.
"""
import time
import json
from hashlib import sha256
from requests import get
from flask import Flask, request
from multiprocessing import Process, Pipe
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")

    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")

    parser.add_argument("--difficulty", type=int, default=5000,
                        help="XXXXXXX")

    parser.add_argument("--myAdd", type=str, default=None,
                        help="YYYYYYYYY")
    arguments, _ = parser.parse_known_args()

    return arguments

arguments = parse_arguments()

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def proof(self):
        """Return the proof of the current block."""
        raise NotImplementedError

    def transactions(self):
        return self.transactions

    def contains(self, transaction):
        return transaction in self.transactions

    def compute_hash(self):
        """
        Returns the hash of the block contents.
        """
        dic = self.__dict__
        dic['transactions'] = [a.__dict__ for a in self.transactions]
        block_string = json.dumps(dic, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Transaction:
    def __init__(self, key, value, origin):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self.key = key
        self.value = value
        self.origin = origin

def create_genesis_block():
    genesis_block = Block(0, [], time.time(), "0")
    #genesis_block.hash = genesis_block.compute_hash()
    return genesis_block

def proof_of_work(blockchain, block):
    start_time = time.time()
    block.nonce = 0
    computed_hash = block.compute_hash()
    while not computed_hash.startswith('0' * DIFF):
        if int((time.time()-start_time) % 60) == 0:
            new_blockchain = consensus(blockchain)
            if new_blockchain:
                # (False: another node got proof first, new blockchain)
                return new_blockchain
        block.nonce += 1
        computed_hash = block.compute_hash()

    new_blockchain = consensus(blockchain)
    if new_blockchain:
        # (False: another node got proof first, new blockchain)
        return new_blockchain
    new_blockchain = add_block(blockchain, block, computed_hash)
    return new_blockchain

def reconstruct_chain(chain):
    init_chain = []
    for block in chain:
        transactions = []

        for t in block["transactions"]:
            transactions.append(Transaction(t["key"], t["value"], t["origin"]))

        new_block = Block(block["index"],
                            transactions,
                            block["timestamp"],
                            block["previous_hash"],
                            block["nonce"])
        init_chain.append(new_block)
    return init_chain

def check_chain_validity(chain):
    """Checks if the current state of the blockchain is valid.
    Meaning, are the sequence of hashes, and the proofs of the
    blocks correct?
    """
    result = True
    #previous_hash = chain[0].compute_hash()
    for i in range(1,len(chain)-1): #start at 1 because previous hash of the block 1 not '0' * DIFF

        #block_hash = block.hash
        # Removes the hash attribute to recompute the hash again using compute_hash.
        #delattr(block, "hash")
        if not is_valid_proof(chain[i], chain[i+1].previous_hash):# or previous_hash != block.previous_hash:
            result = False
            break
        #previous_hash  = block.previous_hash
        #block.hash = block_hash
        #previous_hash = block_hash

    return result

def consensus(blockchain):
    BLOCKCHAIN = blockchain
    curr_len = len(blockchain)
    longest_chain = None

    for node in MINERS:
        response = get("http://" + str(node._address) +"/blockchain")
        length = response.json()["length"]
        chain = reconstruct_chain(response.json()["chain"])
        if length > curr_len and check_chain_validity(chain):
            curr_len = length
            longest_chain = chain

    if longest_chain:
        BLOCKCHAIN = longest_chain
        return BLOCKCHAIN
    return False



def add_transaction(transaction):
    global PENDING_TRANS
    PENDING_TRANS.append(transaction)

def mine(a, blockchain, pending_trans):
    BLOCKCHAIN = blockchain
    PENDING_TRANS = pending_trans

    while True:
        PENDING_TRANS = get(url = 'http://' + str(MY_ADD) +  '/txion')
        PENDING_TRANS = json.loads(PENDING_TRANS)
        if not PENDING_TRANS:
            time.sleep(1)
            continue

        last = BLOCKCHAIN[-1]

        new_block = Block(index=last.index + 1,
                            transactions=PENDING_TRANS,
                            timestamp=time.time(),
                            previous_hash=last.compute_hash())

        BLOCKCHAIN = proof_of_work(BLOCKCHAIN, new_block)
        PENDING_TRANS = []
        a.send(BLOCKCHAIN)
        get(url = 'http://' + str(MY_ADD) +  '/chainUpdated')


def is_valid_proof(block, block_hash):
    return (block_hash.startswith('0' * DIFF) and
            block_hash == block.compute_hash())

def add_block(blockchain, block, proof):
    previous_hash = blockchain[-1].compute_hash()
    if previous_hash != block.previous_hash:
        return False
    if not is_valid_proof(block, proof):
        return False
    block.hash = proof
    blockchain.append(block)
    return blockchain

def get_blocks(self):
    return self._blocks


app = Flask(__name__)

@app.route('/broadcast')
def broadcast():
    msg = request.get_json(force=True)
    transaction = Transaction(msg["k"], msg["v"], msg["o"])
    add_transaction(transaction)
    b.send(PENDING_TRANS)
    print(msg)
    return json.dumps({"deliver": True})

@app.route("/blockchain")
def get_chain():
    chain_data = []
    global BLOCKCHAIN
    print('aaaaaaaaaaaaaaaaaaaaaaa')
    print(BLOCKCHAIN[0].__dict__)
    BLOCKCHAIN = b.recv
    # Returns the blockchain and its length
    for block in BLOCKCHAIN:
        dic = block.__dict__
        dic['transactions'] = [a.__dict__ for a in block.transactions]
        chain_data.append(json.dumps(dic))
    return json.dumps({"length": len(chain_data), "chain": chain_data})

@app.route("/chainUpdated")
def get_chain_updated():
    global BLOCKCHAIN
    BLOCKCHAIN = b.recv
    return

@app.route("/getMiners")
def get_miners():
    return json.dumps({"miners" : MINERS})

@app.route("/getPeers")
def get_peers():
    return json.dumps({"peers" : PEERS})

@app.route("/txion")
def get_txion():
    pending = json.dumps(PENDING_TRANS, sort_keys=True)
    # Empty transaction list
    PENDING_TRANS[:] = []
    return pending

@app.route("/Hi!")
def enterSyst():
    newPeer = request.get_json(force=True)["add"]
    PEERS.append(newPeer)
    if request.get_json(force=True)["miner"]:
        MINERS.append(newPeer)
    return json.dumps({"msg" : 'Welcome Djo ! From Bootstrap\n'})


def welcome_msg():
    print("""       =========================================\n
        BLOCKCHAIN by Guillaume and Laurie\n
       =========================================\n\n """)

def bootstrap():
    """Implements the bootstrapping procedure."""
    global BLOCKCHAIN
    if arguments.bootstrap == arguments.myAdd:
        BLOCKCHAIN = [create_genesis_block()]
        PEERS.append(arguments.myAdd)
    else:
        print(str(arguments.bootstrap) + '\n' + str(arguments.myAdd) + '\n' )
        url = 'http://' + str(arguments.bootstrap) + '/Hi!'
        res = get(url, data = json.dumps({"add": arguments.myAdd, "miner" : arguments.miner}))
        print(res.json()['msg'])
        url = 'http://' + str(arguments.bootstrap) + '/blockchain'
        response = get(url)
        BLOCKCHAIN = reconstruct_chain(response.json()["chain"])



if __name__ == '__main__':

    PENDING_TRANS = []
    PEERS = []
    DIFF = arguments.difficulty
    MINERS = []
    MY_ADD = arguments.myAdd
    bootstrap()
    welcome_msg()
    # Start mining
    a, b = Pipe()
    p1 = Process(target=mine, args=(a, BLOCKCHAIN, PENDING_TRANS))
    p2 = Process(target=app.run(), args=b)
    p2.start()
    if arguments.miner:
        p1.start()
    # Start server to receive transactions


#app.run(host='192.168.1.177', port=80)
