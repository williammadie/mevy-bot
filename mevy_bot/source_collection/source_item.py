from dataclasses import dataclass


@dataclass
class SourceItem:
    """ Class for keeping track of a source in the source inventory"""
    id_source: str
    name: str
    link: str | None = None
    mode: str = "auto"
