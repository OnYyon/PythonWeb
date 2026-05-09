import uuid
from typing import Any, Dict, List
from ..domain.interfaces import IMediaRepository


class MediaServiceApp:
    def __init__(self, repository: IMediaRepository):
        self.repository = repository

    def list_films(self, filters: Dict[str, Any], page: int, page_size: int) -> Dict[str, Any]:
        return self.repository.get_films(filters, page, page_size)

    def get_film_details(self, film_uuid: uuid.UUID) -> Optional[Dict[str, Any]]:
        return self.repository.get_film_by_uuid(film_uuid)

    def create_film(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.repository.create_film(data)

    def update_film(self, film_uuid: uuid.UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.repository.update_film(film_uuid, data)

    def delete_film(self, film_uuid: uuid.UUID) -> None:
        self.repository.delete_film(film_uuid)

    def get_all_genres(self) -> List[Dict[str, Any]]:
        return self.repository.get_genres()

    def create_genre(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.repository.create_genre(data)

    def update_genre(self, genre_uuid: uuid.UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.repository.update_genre(genre_uuid, data)

    def delete_genre(self, genre_uuid: uuid.UUID) -> None:
        self.repository.delete_genre(genre_uuid)

    def get_user_watchlist(self, user_uuid: uuid.UUID, page: int, page_size: int) -> Dict[str, Any]:
        return self.repository.get_watchlist(user_uuid, page, page_size)

    def add_film_to_watchlist(self, user_uuid: uuid.UUID, film_uuid: uuid.UUID) -> Dict[str, Any]:
        return self.repository.add_to_watchlist(user_uuid, film_uuid)

    def remove_from_watchlist(self, watchlist_uuid: uuid.UUID) -> None:
        self.repository.remove_from_watchlist(watchlist_uuid)
