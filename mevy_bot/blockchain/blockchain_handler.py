import os
import logging
from typing import Self
from web3 import Web3

logger = logging.getLogger(__name__)


class BlockchainHandler:

    def __init__(self: Self):
        self.rpc_url = os.environ.get(
            "BLOCKCHAIN_RPC_ENDPOINT_URL")
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

    def healthcheck(self: Self) -> bool:
        return self.web3.is_connected()

    def get_web3(self: Self) -> Web3:
        if not self.web3.is_connected():
            logger.error("Failed to connect to the blockchain.")
            raise ConnectionError("Blockchain connection failed.")
        return self.web3
