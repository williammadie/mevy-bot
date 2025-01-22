
import logging
import os
import pandas as pd
import requests

from mevy_bot.path_finder import PathFinder
from mevy_bot.source_collection.source_inventory import SourceInventory
from mevy_bot.legifrance.law_text_downloader import LawTextDownloader

l = logging.getLogger(__name__)


class SourceRetriever:

    def __init__(self, source_inventory: SourceInventory):
        self.si = source_inventory
        self.law_text_downloader = LawTextDownloader()

    def download_all(self) -> None:
        """ Download all texts"""
        l.info("Downloading all external sources...")
        storage_dir = PathFinder.data_storage()
        for source_id, source in self.si.inventory.items():
            l.info("Retrieving source %s", source.name)
            if source.mode == "manual":
                if pd.isna(source_id) or pd.isna(source.link):
                    l.info("Invalid source %s", source_id)
                    continue

                destination_file = os.path.join(
                    storage_dir, f'{source_id.lower()}.pdf')
                response = requests.get(source.link, stream=True, timeout=60)
                with open(destination_file, 'wb') as f:
                    f.write(response.content)

            if source.mode == "auto":
                self.law_text_downloader.download_code(source.name)

        l.info("All sources have been retrieved")
