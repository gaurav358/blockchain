from functools import reduce
import hashlib as hl

import json
import pickle


from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet


bonus_mining = 10

print(__name__)

class Blockchain:
    
    def __init__(self, curr_node_id):
        Gen_block = Block(0, '', [], 100, 0)
        self.ledger = [Gen_block]
        self.__unloaded_tran = []
        self.load_data()
        self.curr_node = curr_node_id

    
    @property
    def ledger(self):
        return self.__ledger[:]


    @ledger.setter 
    def ledger(self, val):
        self.__ledger = val


    def get_open_transactions(self):
        return self.__unloaded_tran[:]

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:

                data_file = f.readlines()
                block_ledger = json.loads(data_file[0][:-1])
                updated_block_ledger = []
                for block in block_ledger:
                    nonjs_tx = [Transaction(
                        tx['sender'], tx['receiver'], tx['sign'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], nonjs_tx, block['nonce'], block['timestamp'])
                    updated_block_ledger.append(updated_block)
                self.ledger = updated_block_ledger
                unloaded_tran = json.loads(data_file[1])

                updated_unloadeds = []
                for tx in unloaded_tran:
                    updated_unloaded = Transaction(
                        tx['sender'], tx['receiver'], tx['sign'], tx['amount'])
                    updated_unloadeds.append(updated_unloaded)
                self.__unloaded_tran = updated_unloadeds
        except (IOError, IndexError):
            pass
        finally:
            print('all block chain is loaded back from file to normal data')

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                save_ledger = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                    tx.__dict__ for tx in block_el.transactions], block_el.nonce, block_el.timestamp) for block_el in self.__ledger]]
                f.write(json.dumps(save_ledger))
                f.write('\n')
                save_tx = [tx.__dict__ for tx in self.__unloaded_tran]
                f.write(json.dumps(save_tx))
                # save_data = {
                #     'ledger': block_ledger,
                #     'ot': unloaded_tran
                # }
                # f.write(pickle.dumps(save_data))
        except IOError:
            print('data written in file')


    def proof_of_work(self):       
        last_ledger = self.__ledger[-1]
        last_hash = hash_block(last_ledger)
        nonce = 0

        while not Verification.valid_proof(self.__unloaded_tran, last_hash, nonce):
            nonce += 1
        return nonce


    def get_balance(self):
        if self.curr_node == None:
            return None
        owner = self.curr_node
        tx_outgoing = [[tx.amount for tx in block.transactions
                      if tx.sender == owner] for block in self.__ledger]
        open_tx_outgoing = [tx.amount
                          for tx in self.__unloaded_tran if tx.sender == owner]
        tx_outgoing.append(open_tx_outgoing)
        
        amount_outgoing = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_outgoing, 0)
        tx_income = [[tx.amount for tx in block.transactions
                         if tx.receiver == owner] for block in self.__ledger]
        amount_income = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                 if len(tx_amt) > 0 else tx_sum + 0, tx_income, 0)

        return amount_income - amount_outgoing

    def get_last_blockchain_value(self):        
        if len(self.__ledger) < 1:
            return None
        return self.__ledger[-1]


    def add_transaction(self, receiver, sender, sign, amount=1.0):
        if self.curr_node == None:
            return False
        transaction = Transaction(sender, receiver, sign, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__unloaded_tran.append(transaction)
            self.save_data()
            return True
        return False


    def mine_block(self):

        if self.curr_node == None:
            return None
        mine_transac = self.__unloaded_tran[:]
        for tx in mine_transac:
            if not Wallet.verify_transaction(tx):
                return None
        if len(mine_transac)==0:
            return 5
        last_ledger = self.__ledger[-1]
        hashed_block = hash_block(last_ledger)
        nonce = self.proof_of_work()
        reward = Transaction('MINING', self.curr_node, '', bonus_mining)
        mine_transac.append(reward)
        block = Block(len(self.__ledger), hashed_block,
                      mine_transac, nonce)
        self.__ledger.append(block)
        self.__unloaded_tran = []
        self.save_data()
        return block


    def addcoins(self):

        if self.curr_node == None:
            return None
        last_ledger = self.__ledger[-1]
        hashed_block = hash_block(last_ledger)
        reward = Transaction('adding', self.curr_node, '', bonus_mining)
        mine_transac=[]
        mine_transac.append(reward)
        block = Block(len(self.__ledger), hashed_block,
                      mine_transac, 0)
        self.__ledger.append(block)
        self.save_data()
        return block
