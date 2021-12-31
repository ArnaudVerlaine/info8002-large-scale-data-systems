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
import numpy as np

def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")

    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")

    parser.add_argument("--malicious", type=bool, default=False, nargs='?',
                        const=True, help="Defines the node as malicious.")

    parser.add_argument("--difficulty", type=int, default=5,
                        help="XXXXXXX")

    parser.add_argument("--myAdd", type=str, default=None,
                        help="YYYYYYYYY")
    arguments, _ = parser.parse_known_args()

    return arguments

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
        dic = (self.__dict__).copy()

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

    def __str__(self):
        return 'KEY : ' + self.key + '; VALUE : ' + self.value + '; ORIGIN : ' + self.origin + '\n'

def create_genesis_block():
    genesis_block = Block(0, [], time.time(), "0")
    #genesis_block.hash = genesis_block.compute_hash()
    return genesis_block

def proof_of_work(blockchain, block, diff, bootstrap):
    start_time = time.time()
    count = 0
    block.nonce = 0
    computed_hash = block.compute_hash()
    while not computed_hash.startswith('0' * diff):
        if not count % 10**6:
            new_blockchain = consensus(blockchain, diff, bootstrap)
            if new_blockchain:
                # (False: another node got proof first, new blockchain)
                return new_blockchain
        block.nonce += 1
        computed_hash = block.compute_hash()
        count += 1

    new_blockchain = consensus(blockchain, diff, bootstrap)
    if new_blockchain:
        # (False: another node got proof first, new blockchain)
        return new_blockchain
    new_blockchain = add_block(blockchain, block, computed_hash, diff)
    return new_blockchain

def reconstruct_chain(chain):
    init_chain = []
    for block in chain:
        transactions = []
        b = json.loads(block)
        for t in b["transactions"]:
            transactions.append(Transaction(t["key"], t["value"], t["origin"]))

        new_block = Block(b["index"],
                            transactions,
                            b["timestamp"],
                            b["previous_hash"],
                            b["nonce"])
        init_chain.append(new_block)
    return init_chain

def check_chain_validity(chain, diff):
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
        if not is_valid_proof(chain[i], chain[i+1].previous_hash, diff):# or previous_hash != block.previous_hash:
            result = False
            break

        #previous_hash  = block.previous_hash
        #block.hash = block_hash
        #previous_hash = block_hash

    return result

def consensus(blockchain, diff, bootstrap):
    BLOCKCHAIN = blockchain
    curr_len = len(blockchain)
    print('-------------------------len : ' + str(len(blockchain)))
    longest_chain = None
    url = "http://" + str(bootstrap) + "/getMiners"
    MINERS = get(url).json()['miners']
    print('MINERS-----------------------------' + str(MINERS))
    for node in MINERS:
        response = get("http://" + str(node) +"/blockchain")
        length = response.json()["length"]
        print('-------------------------len : ' + str(length))
        chain = reconstruct_chain(response.json()["chain"])
        if length > curr_len and check_chain_validity(chain, diff):
            curr_len = length
            longest_chain = chain

    if longest_chain:
        BLOCKCHAIN = longest_chain
        return BLOCKCHAIN
    return False

# We get the blockchain of every node and we take the longest valid one
def consensus_new_peer(peers, difficulty):
    #curr_len = len(peers)
    curr_len = 0
    longest_chain = None

    for node in peers[:-1]:
        response = get("http://" + str(node) +"/blockchain")
        length = response.json()["length"]
        chain = reconstruct_chain(response.json()["chain"])
        if length > curr_len and check_chain_validity(chain, difficulty):
            curr_len = length
            longest_chain = chain

    return longest_chain

def add_transaction(transaction, rebroad):
    global RECEIVED_TRANS
    global PENDING_TRANS
    if not transaction.origin in RECEIVED_TRANS:
        RECEIVED_TRANS[transaction.origin] = [transaction]
        PENDING_TRANS.append(transaction)
    elif transaction not in RECEIVED_TRANS[transaction.origin]:
        RECEIVED_TRANS[transaction.origin].append(transaction)
        PENDING_TRANS.append(transaction)
    else:
        return
    if rebroad:
        for peer in PEERS:
            url = "http://" + str(peer) + "/broadcast"
            result = get(url, data = json.dumps({"k": transaction.key, "v" : transaction.value, "o": transaction.origin, "rebroad" : "yes"}))
    return



def mine(blockchain, pending_trans, myAdresse, diff, bootstrap, malicious):
    BLOCKCHAIN = blockchain
    PENDING_TRANS = pending_trans
    MY_ADD = myAdresse

    if malicious:
        time.sleep(30) # waits for the blockchain to be filled
        BLOCKCHAIN = consensus(BLOCKCHAIN, diff, bootstrap)
        block_to_modify = len(BLOCKCHAIN) - 3 # decides on a block to modify
        corrupted_chain = []
        index = 0

        while index < len(BLOCKCHAIN): # when we exit the loop, it means that the malicious process has caught up to the miners
            if index < block_to_modify: # we just copy the old blockchain as nothing has changed
                corrupted_chain.append(BLOCKCHAIN[index])
            elif index == block_to_modify: # We reach the block we want to modify
                block = BLOCKCHAIN[index]
                new_block = Block(index=block.index,
                                    transactions=[],
                                    timestamp=block.timestamp,
                                    previous_hash=block.previous_hash)
                corrupted_chain = proof_of_work(corrupted_chain, new_block, diff, bootstrap)
            else:
                block = BLOCKCHAIN[index]
                new_block = Block(index=block.index,
                                    transactions=[],
                                    timestamp=block.timestamp,
                                    previous_hash=corrupted_chain[index-1].compute_hash()) # Since the previous block changed, we need to recompute the hash
                corrupted_chain = proof_of_work(corrupted_chain, new_block, diff, bootstrap)
            index = index + 1
            BLOCKCHAIN = consensus(BLOCKCHAIN, diff, bootstrap) # we get the latest chain

        # Then, the malicious process becomes a regular miner and since it mines faster than the other miners, the corrupted chain will become the longest valid one
        BLOCKCHAIN = corrupted_chain

    while True:
        res = get(url = 'http://' + str(MY_ADD) +  '/txion').json()['pending']
        PENDING_TRANS = [Transaction(t["key"], t["value"], t["origin"]) for t in res]

        if not PENDING_TRANS:
            time.sleep(1)
            continue

        last = BLOCKCHAIN[-1]
        print(last.compute_hash())

        new_block = Block(index=last.index + 1,
                            transactions=PENDING_TRANS,
                            timestamp=time.time(),
                            previous_hash=last.compute_hash())


        BLOCKCHAIN = proof_of_work(BLOCKCHAIN, new_block, diff, bootstrap)
        print('------------ mined --------------------')
        PENDING_TRANS = []

        url = 'http://' + str(MY_ADD) +  '/chainUpdated'
        chain_data = []
        for block in BLOCKCHAIN:
            dic = (block.__dict__).copy()
            dic['transactions'] = [a.__dict__ for a in block.transactions]
            chain_data.append(json.dumps(dic))
        dataChain = json.dumps({"chain": chain_data})
        get(url, data = dataChain)

def heartbeat(myAdd, bootstrap):
    count = {}
    while True:
        url = 'http://' + str(bootstrap) + '/getPeers'
        peers = get(url).json()['peers']

        for i, peer in enumerate(peers):
            print('----------------heartbeat' + str(peer))
            url = 'http://' + str(peer) + '/ping'
            try:
                res = get(url, timeout = 5)
            except:
                res = None
            if not res or res.status_code != 200:
                print
                if i in count:
                    count[i] += 1
                else:
                    count[i] = 1
                if count[i] == 10:
                    url = 'http://' + str(myAdd) + '/delPeer'
                    get(url, data = json.dumps({"peer" : peer}))
            else:
                count[i] = 0
        time.sleep(30)


def is_valid_proof(block, block_hash, diff):
    return (block_hash.startswith('0' * diff) and
            block_hash == block.compute_hash())

def add_block(blockchain, block, proof, diff):
    previous_hash = blockchain[-1].compute_hash()
    if previous_hash != block.previous_hash:
        return False
    if not is_valid_proof(block, proof, diff):
        return False
    blockchain.append(block)
    return blockchain

def get_blocks(self):
    return self._blocks

app = Flask(__name__)

@app.route('/delPeer')
def del_peers():
    peer = request.get_json(force=True)["peer"]
    global PEERS
    global MINERS
    global DEAD_PEERS
    PEERS.remove(peer)
    if peer in MINERS:
        MINERS.remove(peer)
    DEAD_PEERS.append(peer)
    return 'peer removed'

@app.route('/ping')
def ping():
    return 'ok'

@app.route('/broadcast')
def broadcast():
    msg = request.get_json(force=True)
    if "rebroad" in msg or msg["o"] not in DEAD_PEERS:
        rebroad = False
    else:
        rebroad = True
    transaction = Transaction(msg["k"], msg["v"], msg["o"])
    add_transaction(transaction, rebroad)
    #b.send(PENDING_TRANS)
    return json.dumps({"deliver": True})

@app.route("/blockchain")
def get_chain():
    chain_data = []
    global BLOCKCHAIN
    print('BBBBBB' + str(BLOCKCHAIN))
    #BLOCKCHAIN = b.recv
    # Returns the blockchain and its length
    for block in BLOCKCHAIN:
        print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
        dic = (block.__dict__).copy()
        dic['transactions'] = [a.__dict__ for a in block.transactions]
        chain_data.append(json.dumps(dic))

    return json.dumps({"length": len(chain_data), "chain": chain_data})

@app.route("/chainUpdated")
def get_chain_updated():
    global BLOCKCHAIN
    res = request.get_json(force=True)["chain"]
    BLOCKCHAIN = reconstruct_chain(res)
    return 'Chain updated'

@app.route("/peersUpdated")
def get_peers_updated():
    global PEERS
    newPeer = request.get_json(force=True)["peer"]
    PEERS.append(newPeer)
    #PEERS = b.recv
    return ('peersUpdated ok')

@app.route("/minersUpdated")
def get_miners_updated():
    global MINERS
    newMiner = request.get_json(force=True)["miner"]
    MINERS.append(newMiner)
    #PEERS = b.recv
    return ('minersUpdated ok')

@app.route("/getMiners")
def get_miners():
    return json.dumps({"miners" : MINERS})

@app.route("/getPeers")
def get_peers():
    return json.dumps({"peers" : PEERS})

@app.route("/txion")
def get_txion():
    pending = json.dumps({'pending' : [t.__dict__ for t in PENDING_TRANS]})
    # Empty transaction list
    PENDING_TRANS[:] = []
    return pending

@app.route("/testGet")
def testGet():
    Essai = request.get_json(force=True)["add"]
    return json.dumps({"msg" : 'ok'})

@app.route("/retrieve")
def retrieve():
    global BLOCKCHAIN
    print(BLOCKCHAIN)
    difficulty = request.get_json(force=True)["difficulty"]
    bootstrap = request.get_json(force=True)["bootstrap"]
    key = request.get_json(force=True)["key"]
    B2 = consensus(BLOCKCHAIN, difficulty, bootstrap)
    if B2:
        BLOCKCHAIN = B2
    for b in reversed(BLOCKCHAIN):
        for t in b.transactions:
            if t.key == key:
                return json.dumps({"value" : t.value})
    return json.dumps({"value" : None})

@app.route("/retrieve_all")
def retrieve_all():
    global BLOCKCHAIN
    difficulty = request.get_json(force=True)["difficulty"]
    bootstrap = request.get_json(force=True)["bootstrap"]
    key = request.get_json(force=True)["key"]
    B2 = consensus(BLOCKCHAIN, difficulty, bootstrap)
    if B2:
        BLOCKCHAIN = B2
    values = []
    for b in reversed(BLOCKCHAIN):
        for t in b.transactions:
            if t.key == key:
                values.append(t.value)
    return json.dumps({"values" : values})

@app.route("/Hi!")
def enterSyst():
    newPeer = request.get_json(force=True)["add"]
    newMiner = request.get_json(force=True)["miner"]
    if newMiner:
        for miner in MINERS: #all except bootstrap & new peer
            switch = 1
            if arguments.miner and switch:
                switch = 0
                continue
            url = "http://" + str(miner) + "/minersUpdated"
            result = get(url, data = json.dumps({"miner": newPeer}))
        MINERS.append(newPeer)


    #if request.get_json(force=True)["miner"]:
    #    MINERS.append(newPeer)

    # When a new node enters the system, we send the update to every other node.
    for peer in PEERS[1:]: #all except bootstrap & new peer
        url = "http://" + str(peer) + "/peersUpdated"
        result = get(url, data = json.dumps({"peer": newPeer}))
    PEERS.append(newPeer)
    return json.dumps({"peersList" : PEERS, "minersList" : MINERS})


def welcome_msg():
    print("""       =========================================\n
        BLOCKCHAIN by Guillaume and Laurie \n
        =========================================\n\n """)

def bootstrap(diff):
    """Implements the bootstrapping procedure."""
    global BLOCKCHAIN
    global PEERS
    global MINERS
    if arguments.bootstrap == arguments.myAdd:
        BLOCKCHAIN = [create_genesis_block()]
        PEERS.append(arguments.myAdd)
        if arguments.miner:
            MINERS.append(arguments.myAdd)
    else:
        #url = 'http://' + str(arguments.bootstrap) + '/testGet'
        url = 'http://' + str(arguments.bootstrap) + '/Hi!'
        res = get(url, data = json.dumps({"add": arguments.myAdd, "miner" : arguments.miner}))
        PEERS = res.json()['peersList']
        MINERS = res.json()['minersList']
        BLOCKCHAIN = consensus_new_peer(PEERS, diff) # When a new peer arrives, it does a consensus with the other peers
        #url = 'http://' + str(arguments.bootstrap) + '/blockchain'
        #response = get(url)
        #BLOCKCHAIN = reconstruct_chain(response.json()["chain"])


if __name__ == '__main__':
    arguments = parse_arguments()
    PENDING_TRANS = []
    RECEIVED_TRANS = {}
    PEERS = []
    MINERS = []
    DEAD_PEERS = []
    MY_ADD = arguments.myAdd
    diff = arguments.difficulty
    mal = arguments.malicious
    bootstrap(diff)
    welcome_msg()

    # Start mining
    #a, b = Pipe()
    p1 = Process(target=mine, args=(BLOCKCHAIN, PENDING_TRANS, MY_ADD, diff, arguments.bootstrap, mal))
    p3 = Process(target=heartbeat, args =(MY_ADD, arguments.bootstrap))

    #p2.start()
    if arguments.miner:
        p1.start()
    p3.start()
    p2 = Process(target=app.run(host=MY_ADD.split(':')[0], port=MY_ADD.split(':')[1]))
    # Start server to receive transactions

#app.run(host='192.168.1.177', port=80)

