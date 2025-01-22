from dataclasses import dataclass


@dataclass
class SourceItem:
    """ Class for keeping track of a source in the source inventory"""
    id_source: str
    id_scheme: str | None
    text_type: str | None
    name: str
    description: str | None
    link: str | None
    mode: str
