import os
import logging
import pandas as pd
from typing import Dict

from mevy_bot.path_finder import PathFinder
from mevy_bot.source_collection.source_item import SourceItem

l = logging.getLogger(__name__)

class SourceInventory:

    def __init__(self) -> None:
        self.sources: list = self.load_source_referential()
        self.inventory: Dict[str, SourceItem] = self.build_source_inventory()

    def load_source_referential(self) -> list:
        l.info("Loading source referential...")
        source_referential = os.path.join(
            PathFinder.data_definition(),
            "s1.csv"
        )
        df = pd.read_csv(source_referential, encoding='utf8')
        l.info("Source referential successfully loaded!")
        return df.to_dict('records')

    def build_source_inventory(self) -> Dict[str, SourceItem]:
        l.info("Building source inventory...")
        inventory = dict()
        for source in self.sources:
            source_id = source["identifier_name"]
            source_item = SourceItem(
                source_id,
                source["identifier_scheme"],
                source["type"],
                source["name"],
                source["description"],
                source["link"]
            )
            inventory[source_id] = source_item
        l.info("Source inventory successfully built!")
        return inventory
