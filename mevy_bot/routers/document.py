from http import HTTPStatus
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from mevy_bot.authentication.authentication_handler import AuthenticationHandler
from mevy_bot.authentication.cookie_authentication import CookieAuthentication
from mevy_bot.blockchain.blockchain_handler import BlockchainHandler
from mevy_bot.models.blockchain import DocumentMetadata
from mevy_bot.services.document_verifier_service import DocumentVerifierService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document", tags=["Document Verifier"])
blockchain_handler = BlockchainHandler()
document_service = DocumentVerifierService(blockchain_handler)

# 100 MB in bytes
MAX_FILE_SIZE = 1 * 1024 * 1024     # 104,857,600 bytes


def ensure_file_can_be_handled(file: UploadFile) -> None:
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


@router.post("/", dependencies=[Depends(CookieAuthentication())])
async def upload_document(
    file: UploadFile,
    token: str = Depends(CookieAuthentication())
):
    # Raise error if file cannot be handled
    ensure_file_can_be_handled(file)

    # Retrieve current user id (= the email address)
    payload = AuthenticationHandler.decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail="Invalid token payload")
    user_id = str(payload.get("user_id"))

    try:
        # Compute file hash
        file_bytes = await file.read()
        document_hash = blockchain_handler.get_web3().keccak(file_bytes)

        # Build document metadata
        document_metadata = DocumentMetadata(
            document_hash=document_hash.hex(),
            author_username=user_id,
            document_title=file.filename,   # type: ignore
            last_modified_timestamp=int(
                datetime.now(tz=timezone.utc).timestamp())
        )

        document_service.set_document_metadata(
            document_hash,
            document_metadata
        )

        return {"filename": file.filename, "size": file.size}
    except ConnectionError as err:
        logger.error("Connection error while uploading document: %s", err)
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail={"reason": "Blockchain network is unreachable"}
        ) from err


@router.post("/verification", dependencies=[Depends(CookieAuthentication())])
async def verify_document(file: UploadFile):
    # Raise error if file cannot be handled
    ensure_file_can_be_handled(file)

    try:
        # Compute file hash
        file_bytes = await file.read()
        document_hash = blockchain_handler.get_web3().keccak(file_bytes)

        # Retrieve document metadata from the blockchain
        metadata = document_service.get_document_metadata(document_hash)
        return metadata
    except ConnectionError as err:
        logger.error("Connection error while verifying document: %s", err)
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail={"reason": "Blockchain network is unreachable"}
        ) from err
    except FileNotFoundError as err:
        logger.info("Document not found in blockchain: %s", document_hash.hex())
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"reason": "Document not found in blockchain"}
        ) from err
