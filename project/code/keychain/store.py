"""
KeyChain key-value store (stub).
NB: Feel free to extend or modify.
"""
from keychain import Transaction
import subprocess
from requests import get
import json

class Callback:
    def __init__(self, transaction, chain):
        self._transaction = transaction
        self._chain = chain

    def wait(self):
        """Wait until the transaction appears in the blockchain."""
        raise NotImplementedError

    def completed(self):
        """Polls the blockchain to check if the data is available."""
        raise NotImplementedError


class Storage:
    def __init__(self, bootstrap, miner, difficulty):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """

        self.myAdd = '127.0.0.1:5000'
        self.bootstrap = bootstrap
        #self._blockchain = Blockchain(bootstrap, difficulty)
        #hello = subprocess.Popen(["python" ,"blockchain_app.py", "--bootstrap", str(bootstrap), "--miner", str(miner),  "--difficulty", str(difficulty)])
        hello = subprocess.Popen(["python" ,"keychain/blockchain.py", "--bootstrap", str(bootstrap), "--miner", str(miner),  "--difficulty", str(difficulty), "--myAdd", str(self.myAdd)])


         #check 200
         # copie chaine au bootstrap

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.
        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        transaction = Transaction(key, value, 'origin')
        self.broadcast(self.bootstrap, transaction)

        #callback = Callback(transaction, self._blockchain)
        if block:
            callback.wait()

        #return callback

    def retrieve(self, key):
        """Searches the most recent value of the specified key.
        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
        raise NotImplementedError

    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        raise NotImplementedError

    def get_chain(self):
        url = "http://" + str(self.myAdd) + "/blockchain"
        result = get(url)
        return result.json()['chain']

    def broadcast(self, bootstrap, transaction):
        url = "http://" + str(bootstrap) + "/getPeers"
        print('cccccccccccccccccccccccccccccccccccccccccccccccccccccc')
        peers = get(url).json()['peers']
        print(peers)
        print('cccccccccccccccccccccccccccccccccccccccccccccccccccccc')
        #check if 200
        for peer in peers:
            url = "http://" + str(peer) + "/broadcast"
            result = get(url, data = json.dumps({"k": transaction.key, "v" : transaction.value, "o": transaction.origin}))
            #check if 200
