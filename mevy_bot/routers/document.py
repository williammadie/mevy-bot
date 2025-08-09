from http import HTTPStatus
import logging

from fastapi import APIRouter, HTTPException, UploadFile

from mevy_bot.blockchain.blockchain_handler import BlockchainHandler
from mevy_bot.models.blockchain import DocumentMetadata
from mevy_bot.services.document_verifier_service import DocumentVerifierService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document-verifier", tags=["Document Verifier"])
blockchain_handler = BlockchainHandler()
document_service = DocumentVerifierService(blockchain_handler)

# 100 MB in bytes
MAX_FILE_SIZE = 1 * 1024 * 1024     # 104,857,600 bytes


@router.post("/")
async def upload_document(file: UploadFile):

    if file.size is None or file.filename is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"reason": "bad file format"}
        )

    if file.size is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"reason": "file size exceeds 1 GB"}
        )

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"reason": "file must be a PDF"}
        )

    document_metadata = DocumentMetadata(
        author_username="john doe",
        document_title=file.filename,
        last_modified_timestamp=int(file.headers.get('last-modified', 0))
    )

    # Compute file hash
    file_bytes = await file.read()
    document_hash = blockchain_handler.get_web3().keccak(file_bytes)

    document_service.set_document_metadata(
        document_hash,
        document_metadata
    )

    return {"filename": file.filename, "size": file.size}
