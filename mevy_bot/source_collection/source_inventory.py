import os
import json
import logging
from typing import Dict, Self

import pandas as pd
from unidecode import unidecode

from mevy_bot.path_finder import PathFinder
from mevy_bot.source_collection.source_item import SourceItem

l = logging.getLogger(__name__)


class SourceInventory:

    def __init__(self) -> None:
        self.ensure_directories_exist()
        self.manual_sources: list = self.load_manual_source_referential()
        self.auto_sources: list = self.load_auto_sources()
        self.inventory: Dict[str, SourceItem] = self.build_source_inventory()
    
    def ensure_directories_exist(self) -> None:
        """ Create mandatory directories if missing """
        os.makedirs(PathFinder.data_storage_auto(), exist_ok=True)
        os.makedirs(PathFinder.data_storage_manual(), exist_ok=True)

    def load_manual_source_referential(self) -> list:
        l.info("Loading source referential...")
        source_referential = os.path.join(
            PathFinder.data_definition(),
            "manual_sources.csv"
        )
        df = pd.read_csv(source_referential, encoding='utf8')
        l.info("Source referential successfully loaded!")
        return df.to_dict('records')

    def build_source_inventory(self) -> Dict[str, SourceItem]:
        l.info("Building source inventory...")
        inventory = dict()
        for source in self.manual_sources:
            source_id = unidecode(source["name"]).replace(' ', '_')
            source_item = SourceItem(
                id_source=source_id,
                name=source["name"],
                link=source["link"],
                mode="manual"
            )
            inventory[source_id] = source_item

        for source in self.auto_sources:
            source_id = unidecode(source["name"]).replace(' ', '_')
            source_item = SourceItem(
                id_source=source_id,
                name=source["name"]
            )
            inventory[source_id] = source_item

        l.info("Source inventory successfully built!")
        return inventory

    def load_auto_sources(self: Self) -> list:
        data_storage_path = PathFinder.data_definition()
        filepath = os.path.join(data_storage_path, 'auto_sources.json')

        with open(filepath, mode='r', encoding='utf8') as f:
            raw_content = f.read()
            sources_dict = json.loads(raw_content)

        sources = []
        for code in sources_dict['codes']:
            d = {"name": code}
            sources.append(d)

        return sources
