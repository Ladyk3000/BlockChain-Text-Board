from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4


class NodeRegisterRequest(BaseModel):
    nodes: list[str]


class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    message: str


class ApiWrap:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.app = FastAPI()
        self.node_identifier = str(uuid4()).replace('-', '')

        self.setup_routes()

    def setup_routes(self):
        self.app.post('/nodes/register')(self.register_nodes)
        self.app.get('/nodes/resolve')(self.consensus)
        self.app.get('/mine')(self.mine)
        self.app.post('/transactions/new')(self.new_transaction)
        self.app.get('/chain')(self.full_chain)

    def register_nodes(self, data: NodeRegisterRequest):
        nodes = data.nodes
        if not nodes:
            return "Error: Please supply a valid list of nodes", 400
        for node in nodes:
            self.blockchain.register_node(node)

        response = {
            'message': 'New nodes have been added',
            'total nodes': list(self.blockchain.nodes),
        }
        return response

    def consensus(self):
        replaced = self.blockchain.resolve_conflicts()
        if replaced:
            response = {
                'message': 'Chain was replaced',
                'new_chain': self.blockchain.chain
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain': self.blockchain.chain
            }
        return response

    def mine(self):
        last_block = self.blockchain.last_block
        last_proof = last_block['proof']
        proof = self.blockchain.proof_of_work(last_proof)
        self.blockchain.new_transaction(sender='0',
                                        recipient=self.node_identifier,
                                        message='')
        previous_hash = self.blockchain.hash(last_block)
        block = self.blockchain.new_block(proof, previous_hash)
        response = {
            'message': 'New Block Forged',
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        return response

    def new_transaction(self, data: TransactionRequest):
        sender = data.sender
        recipient = data.recipient
        message = data.message
        index = self.blockchain.new_transaction(sender, recipient, message)
        response = {'message': f'Transaction will be added to Block {index}'}
        return response

    def full_chain(self):
        response = {
            'chain': self.blockchain.chain,
            'length': len(self.blockchain.chain),
        }
        return response
