import os
import logging
from typing import Self
from web3 import Web3

logger = logging.getLogger()


class BlockchainHandler:

    def __init__(self: Self):
        self.blockchain_rpc_endpoint_url = os.environ.get(
            "BLOCKCHAIN_RPC_ENDPOINT_URL",)
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_rpc_endpoint_url))

    def healthcheck(self: Self) -> bool:
        return self.web3.is_connected()
