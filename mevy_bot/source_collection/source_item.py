from dataclasses import dataclass


@dataclass
class SourceItem:
    """ Class for keeping track of a source in the source inventory"""
    id_source: str
    id_scheme: str
    text_type: str
    name: str
    description: str
    link: str
