from dataclasses import dataclass

@dataclass
class DocumentMetadata:
    author_username: str
    document_title: str
    last_modified_timestamp: int
