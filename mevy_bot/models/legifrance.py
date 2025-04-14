from __future__ import annotations  # For recursive pydantic models
from typing import List
from pydantic import BaseModel


class Article(BaseModel):
    id: str
    cid: str
    etat: str
    num: str | None
    content: str
    intOrdre: int


class Section(BaseModel):
    id: str
    cid: str
    title: str
    etat: str
    intOrdre: int
    articles: List[Article]
    sections: List[Section]


class Code(BaseModel):
    id: str
    cid: str
    title: str
    jurisState: str
    nature: str
    sections: List[Section]

class Law(BaseModel):
    id: str
    cid: str
    title: str
    modifDate: str
    nature: str
    sections: List[Section]