import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional


@dataclass
class GenreEntity:
    uuid: uuid.UUID
    name: str
    description: Optional[str]


@dataclass
class FilmEntity:
    uuid: uuid.UUID
    title: str
    description: Optional[str]
    release_date: date
    duration: int
    poster_url: Optional[str]
    genres: List[GenreEntity]


@dataclass
class WatchlistItemEntity:
    uuid: uuid.UUID
    film: FilmEntity
    added_at: datetime
