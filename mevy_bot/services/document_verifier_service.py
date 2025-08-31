import os
import json
import logging
from typing import Self

from web3.contract import Contract

from mevy_bot.blockchain.blockchain_handler import BlockchainHandler
from mevy_bot.models.blockchain import DocumentMetadata

CONTRACT_ABI = json.loads("""
[
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "name": "documents",
      "outputs": [
        {
          "internalType": "string",
          "name": "authorUsername",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "documentTitle",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "lastModifiedTimestamp",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "documentHash",
          "type": "bytes32"
        }
      ],
      "name": "ensureDocumentExists",
      "outputs": [],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "documentHash",
          "type": "bytes32"
        }
      ],
      "name": "getDocumentMetadata",
      "outputs": [
        {
          "internalType": "string",
          "name": "authorUsername",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "documentTitle",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "lastModifiedTimestamp",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "documentHash",
          "type": "bytes32"
        },
        {
          "internalType": "string",
          "name": "authorUsername",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "documentTitle",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "lastModifiedTimestamp",
          "type": "uint256"
        }
      ],
      "name": "setDocumentMetadata",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
""")
GAS_BUFFER = 10000


class DocumentVerifierService:

    def __init__(self: Self, blockchain_handler: BlockchainHandler):
        self.blockchain_handler = blockchain_handler
        self.contract_address = os.environ.get(
            "BLOCKCHAIN_DOCUMENT_VERIFIER_CONTRACT_ADDRESS")
        if not self.contract_address:
            raise ValueError(
                "BLOCKCHAIN_DOCUMENT_VERIFIER_CONTRACT_ADDRESS is not set in the environment variables.")

        self.account_address = os.environ.get(
            "BLOCKCHAIN_ACCOUNT_ADDRESS")
        if not self.account_address:
            raise ValueError(
                "BLOCKCHAIN_ACCOUNT_ADDRESS is not set in the environment variables.")

        self.account_private_key = os.environ.get(
            "BLOCKCHAIN_ACCOUNT_PRIVATE_KEY")
        if not self.account_private_key:
            raise ValueError(
                "BLOCKCHAIN_ACCOUNT_PRIVATE_KEY is not set in the environment variables.")

    def get_contract(self: Self) -> Contract:
        return self.blockchain_handler.get_web3().eth.contract(    # type: ignore
            address=self.contract_address,  # type: ignore
            abi=CONTRACT_ABI
        )

    def get_document_metadata(
        self: Self,
        document_hash: bytes,
    ) -> DocumentMetadata:
        try:
            author, title, timestamp = self.get_contract().functions.getDocumentMetadata(
                document_hash).call()
        except Exception as e:
            logging.error(f"Error fetching document metadata: {e}")

        try:
            return DocumentMetadata(
                document_hash=document_hash.hex(),
                author_username=author,
                document_title=title,
                last_modified_timestamp=timestamp
            )
        except UnboundLocalError as err:
            raise FileNotFoundError(
                f"No record found for document hash: {document_hash.hex()}"
            ) from err

    def set_document_metadata(
        self: Self, document_hash,
        document_metadata: DocumentMetadata
    ) -> None:

        # Estimate gas for the transaction
        estimated_gas = self.get_contract().functions.setDocumentMetadata(
            document_hash,
            document_metadata.author_username,
            document_metadata.document_title,
            document_metadata.last_modified_timestamp
        ).estimate_gas({'from': self.account_address})  # type: ignore

        # Build the transaction
        tx = self.get_contract().functions.setDocumentMetadata(
            document_hash,
            document_metadata.author_username,
            document_metadata.document_title,
            document_metadata.last_modified_timestamp
        ).build_transaction({
            'from': self.account_address,  # type: ignore
            'nonce': self.blockchain_handler.get_web3().eth.get_transaction_count(self.account_address),
            'gas': estimated_gas + GAS_BUFFER,
            'gasPrice': self.blockchain_handler.get_web3().eth.gas_price
        })

        # Sign the transaction
        signed_tx = self.blockchain_handler.get_web3().eth.account.sign_transaction(
            tx,
            private_key=self.account_private_key
        )

        # Send the transaction
        tx_hash = self.blockchain_handler.get_web3().eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        # Wait for receipt
        receipt = self.blockchain_handler.get_web3(
        ).eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction mined in block: {receipt}")
