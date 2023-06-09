import uvicorn

from BlockChain import BlockChain
from ApiWrap import ApiWrap

if __name__ == '__main__':
    blockchain = BlockChain()
    app_wrapper = ApiWrap(blockchain)
    app = app_wrapper.app
    uvicorn.run(app, host="127.0.0.1", port=8000)
