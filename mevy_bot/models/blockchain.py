from dataclasses import dataclass


@dataclass
class DocumentMetadata:
    document_hash: str | None
    author_username: str
    document_title: str
    last_modified_timestamp: int
