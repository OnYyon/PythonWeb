import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IMediaRepository(ABC):
    # Films
    @abstractmethod
    def get_films(
        self, filters: Dict[str, Any], page: int, page_size: int
    ) -> Dict[str, Any]:
        """Возвращает список фильмов с учетом фильтров и пагинации"""
        pass

    @abstractmethod
    def get_film_by_uuid(self, film_uuid: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Возвращает один фильм по UUID"""
        pass

    @abstractmethod
    def create_film(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает новый фильм"""
        pass

    @abstractmethod
    def update_film(self, film_uuid: uuid.UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновляет данные фильма"""
        pass

    @abstractmethod
    def delete_film(self, film_uuid: uuid.UUID) -> None:
        """Удаляет фильм"""
        pass

    # Genres
    @abstractmethod
    def get_genres(self) -> List[Dict[str, Any]]:
        """Возвращает список всех жанров"""
        pass

    @abstractmethod
    def create_genre(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает новый жанр"""
        pass

    @abstractmethod
    def update_genre(
        self, genre_uuid: uuid.UUID, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновляет жанр"""
        pass

    @abstractmethod
    def delete_genre(self, genre_uuid: uuid.UUID) -> None:
        """Удаляет жанр"""
        pass

    # Watchlist
    @abstractmethod
    def get_watchlist(
        self, user_uuid: uuid.UUID, page: int, page_size: int
    ) -> Dict[str, Any]:
        """Возвращает список просмотра конкретного пользователя"""
        pass

    @abstractmethod
    def add_to_watchlist(
        self, user_uuid: uuid.UUID, film_uuid: uuid.UUID
    ) -> Dict[str, Any]:
        """Добавляет фильм в список просмотра пользователя"""
        pass

    @abstractmethod
    def remove_from_watchlist(self, watchlist_uuid: uuid.UUID) -> None:
        """Удаляет запись из списка просмотра"""
        pass
