import os
import io
from typing import Self, List

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from mevy_bot.path_finder import PathFinder


class GdriveService:

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

    def list_knowledge_files(self: Self) -> dict:
        folder_id = self.get_knowledge_folder_id()
        raw_query = f"'{folder_id}' in parents"
        # pylint: disable=maybe-no-member
        results = self.service.files().list(
            q=raw_query,
            fields="files(id, name)"
        ).execute()
        return results

    def get_knowledge_folder_id(self: Self) -> str:
        raw_query = f"mimeType = '{self.KNOWLEDGE_FOLDER_MIMETYPE}' and name = '{self.KNOWLEDGE_FOLDER_NAME}'"
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
        target_dir: str
    ) -> None:
        file_content = self.download_file(file_id)
        self.write_file(file_content, file_name, target_dir)

    def download_file(self: Self, file_id: str) -> bytes:
        try:
            # pylint: disable=maybe-no-member
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}.")

        except HttpError as error:
            print(f"An error occurred: {error}")
            file = None

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
