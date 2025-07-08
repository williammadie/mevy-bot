import logging
import os
import io
from typing import Self

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from mevy_bot.file_reader import FileReader
from mevy_bot.path_finder import PathFinder

logger = logging.getLogger(__name__)


class GdriveService:

    META_FOLDER_NAME = "mevy_meta"
    KNOWLEDGE_FOLDER_NAME = "mevy_files"
    KNOWLEDGE_FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
    KNOWLEDGE_FOLDER_METADATA = {
        'name': KNOWLEDGE_FOLDER_NAME,
        'parents': ['1XqXbJraZyoCyeECESXA6sDUUO7ba7ttZ'],
        'mimeType': KNOWLEDGE_FOLDER_MIMETYPE
    }

    def __init__(self: Self) -> None:
        credentials_filepath = os.path.join(
            PathFinder.secrets(), 'credentials.json')
        credentials = service_account.Credentials.from_service_account_file(
            credentials_filepath,
            scopes=[
                'https://www.googleapis.com/auth/drive'
            ]
        )
        self.service = build("drive", "v3", credentials=credentials)

    def retrieve_meta_file(self: Self) -> str:
        """ Retrieve meta file (one maximum)"""
        folder_id = self.get_folder_id(self.META_FOLDER_NAME)
        results = self.list_files_in_folder(folder_id)
        if "files" not in results:
            logger.error("No files in meta folder.")
        files = results["files"]

        if len(files) == 0:
            logger.error("No files in meta folder")
        meta_file = files[0]
        print(meta_file)

        if "id" not in meta_file:
            logger.error("Meta file does not have an ID.")

        raw_binary_content = self.download_file(
            meta_file["id"], meta_file["mimeType"])
        
        return raw_binary_content.decode("utf-8")

    def list_knowledge_files(self: Self) -> dict:
        folder_id = self.get_folder_id(self.KNOWLEDGE_FOLDER_NAME)
        return self.list_files_in_folder(folder_id)

    def list_files_in_folder(self: Self, folder_id: str) -> dict:
        raw_query = f"'{folder_id}' in parents"
        # pylint: disable=maybe-no-member
        results = self.service.files().list(
            q=raw_query,
            fields="files(id, name, modifiedTime, mimeType)"
        ).execute()
        return results

    def get_folder_id(self: Self, folder_name: str) -> str:
        raw_query = f"mimeType = '{self.KNOWLEDGE_FOLDER_MIMETYPE}' and name = '{folder_name}'"
        # pylint: disable=maybe-no-member
        matching_folders = self.service.files().list(
            q=raw_query,
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        matching_folder_ids = matching_folders.get("files", [])
        return matching_folder_ids[0].get("id")

    def download_and_write_file(
        self: Self,
        file_id: str,
        file_name: str,
        file_mime_type: str,
        target_dir: str
    ) -> None:
        file_content = self.download_file(file_id, file_mime_type)
        self.write_file(file_content, file_name, target_dir)

    def download_file(self: Self, file_id: str, file_mime_type: str) -> bytes:
        logging.info("Trying to download file %s (mimeType: %s)", file_id, file_mime_type)
        try:
            if file_mime_type == "application/vnd.google-apps.document":
                # Export Google Docs as PDF
                # pylint: disable=maybe-no-member
                request = self.service.files().export_media(
                    fileId=file_id, mimeType="text/plain"
                )
            else:
                # Download binary file directly
                # pylint: disable=maybe-no-member
                request = self.service.files().get_media(fileId=file_id)

            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logging.info("Download %s.", int(status.progress() * 100))

        except HttpError as error:
            logging.error("Unknown error : %s", error)
            return bytes()

        return file.getvalue()

    def write_file(
        self: Self,
        file_content: bytes,
        file_name: str,
        target_dir: str
    ) -> None:
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, 'wb') as fp:
            fp.write(file_content)
