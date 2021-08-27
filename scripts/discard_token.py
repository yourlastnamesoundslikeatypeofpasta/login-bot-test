import pprint
import random
import hashlib
import json
import string
import time


class DiscardToken:
    def __init__(self):
        self.genesis_hash = self.hash_str('DISARDDDD DOLLARRRR TO THE MOONNNNNN!🚀')
        self.genesis_block = {
            'index': 1,
            "timestamp": time.time(),
            'transactions': [
                {
                    'sender': "genes_wallet",
                    'recipient': "the_kings_wallet",
                    'amount': 99999999999999,
                }
            ],
            'previous_hash': self.genesis_hash
        }
        self.chain = [self.genesis_block]
        self.current_trans = []

    def add_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }
        sender_balance = self.get_wallet_amount(sender)
        if sender_balance > amount:
            self.current_trans.append(transaction)
            return
        return print('Transaction Denied: Insufficient Balance')

    def add_block(self):
        block = {
            'index': len(self.chain) + 1,
            "timestamp": time.time(),
            'transactions': [
            ],
            'previous_hash': self.get_last_block_hash()
        }

        # move current transactions to block transactions lst & add block to chain
        if self.current_trans:
            while self.current_trans:
                block['transactions'].append(self.current_trans.pop())
            self.chain.append(block)

    def is_chain_valid(self):
        previous_block = None
        for block in self.chain:
            # validate block 1
            if block['index'] == 1:
                if block['previous_hash'] == self.genesis_hash:
                    previous_block = block
                    continue

            # validate other blocks
            previous_block_hash = self.get_block_hash(previous_block)
            if previous_block_hash == block['previous_hash']:
                previous_block = block
                continue
            else:
                print(block)
                return False
        return True

    def get_last_block_hash(self):
        last_block = self.chain[-1]
        block_string = json.dumps(last_block, sort_keys=True).encode()
        previous_block_hash = hashlib.sha256(block_string).hexdigest()
        return previous_block_hash

    def get_chain(self):
        return self.chain

    def get_wallet_amount(self, address):
        amount_received = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['recipient'] == address:
                    amount_received += transaction['amount']

        amount_sent = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == address:
                    amount_sent += transaction['amount']
        wallet_balance = amount_received - amount_sent
        return wallet_balance

    @staticmethod
    def create_wallet():
        wallet_address = ''.join(random.choices(string.ascii_letters + string.digits, k=random.choice([i for i in range(25, 36)])))
        return wallet_address

    @staticmethod
    def hash_str(string):
        string_to_hash = json.dumps(string, sort_keys=True).encode()
        string_hash = hashlib.sha256(string_to_hash).hexdigest()
        return string_hash

    @staticmethod
    def get_block_hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        block_hash = hashlib.sha256(block_string).hexdigest()
        return block_hash


# usage
'''
# initiate chain
init_chain = DiscardToken()

# create test wallet
wallet = init_chain.create_wallet()

# show original balances
print('original balances')
print(init_chain.get_wallet_amount('the_kings_wallet'))
print(init_chain.get_wallet_amount(wallet))
print('-' * 10)

# send 10 from the kings wallet to wallet address
print('send 10 from the kings wallet to wallet address')
init_chain.add_transaction('the_kings_wallet', wallet, 10)
init_chain.add_block()
if init_chain.is_chain_valid():
    print(init_chain.get_wallet_amount('the_kings_wallet'))
    print(init_chain.get_wallet_amount(wallet))
print('-' * 10)

# send 15000 from wallet to the kings wallet, (should throw insufficient funds error)
print('send 15000 from wallet to the kings wallet, (should throw insufficient funds error)')
init_chain.add_transaction(wallet, 'the_kings_wallet', 150000)
init_chain.add_block()
if init_chain.is_chain_valid():
    print(init_chain.get_wallet_amount('the_kings_wallet'))
    print(init_chain.get_wallet_amount(wallet))

# NOTE: if a user would like to send tokens, they need to be granted tokens from 'the_kings_wallet' first

# create fake transactions, add them to a block, add the block to the chain, validate chain
number_of_transactions = 5000
number_of_transactions_per_block = 10
time_start = time.time()
for i in range(number_of_transactions):
    random_sender = ''.join(random.choices(string.ascii_letters + string.digits, k=random.choice([i for i in range(25, 36)]))) # create 25 char address
    random_receiver = ''.join(random.choices(string.ascii_letters + string.digits, k=random.choice([i for i in range(25, 36)]))) # create 25 char address
    random_amount = random.randint(1, 10000)
    init_chain.add_transaction(random_sender, random_receiver, random_amount)
    if i % number_of_transactions_per_block == 0:
        init_chain.add_block()
        if init_chain.is_chain_valid():
            continue
        else:
            print('Chain is invalid')
            break
time_end = time.time()
process_time = time_end - time_start
print(f'Time to process {number_of_transactions} transactions with {number_of_transactions_per_block} transactions/block; {process_time} seconds')

if init_chain.is_chain_valid():
    print('All blocks validated')
    pprint.pprint(init_chain.chain[-1])
'''
