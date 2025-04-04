import os
import logging
import json
from typing import Self

from mevy_bot.path_finder import PathFinder

logger = logging.getLogger()


class GdriveCacheService:

    def __init__(self: Self) -> None:
        data_storage = PathFinder.data_storage()
        self.cache_file = os.path.join(data_storage, "gdrive_known_files.json")

    def write(self: Self, new_cache: dict) -> None:
        cache = json.dumps(new_cache)

        with open(self.cache_file, "w", encoding="utf8") as f:
            logger.info("Updating cache file %s...", self.cache_file)
            f.write(cache)

        logger.info("Cache file updated..")

    def read(self: Self) -> dict:
        try:
            with open(self.cache_file, "r", encoding="utf8") as f:
                cache_file_content = f.read()
            return json.loads(cache_file_content)
        except FileNotFoundError:
            return {}
