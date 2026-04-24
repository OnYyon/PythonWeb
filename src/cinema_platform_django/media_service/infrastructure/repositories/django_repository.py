import uuid
from typing import Any, Dict, List, Optional
from django.core.paginator import Paginator
from ...domain.repositories.interfaces import IMediaRepository
from ...infrastructure.models import Film, Genre, Watchlist


class DjangoMediaRepository(IMediaRepository):
    def _serialize_genre(self, genre: Genre) -> Dict[str, Any]:
        return {
            "uuid": genre.uuid,
            "name": genre.name,
            "description": genre.description,
        }

    def _serialize_film(self, film: Film) -> Dict[str, Any]:
        return {
            "uuid": film.uuid,
            "title": film.title,
            "description": film.description,
            "release_date": film.release_date,
            "duration": film.duration,
            "poster_url": film.poster_url,
            "genres": [self._serialize_genre(g) for g in film.genres.all()]
        }

    def get_films(self, filters: Dict[str, Any], page: int, page_size: int) -> Dict[str, Any]:
        queryset = Film.objects.prefetch_related('genres').all()

        # Фильтрация
        if 'genre' in filters and filters['genre']:
            queryset = queryset.filter(genres__uuid=filters['genre'])
        if 'search' in filters and filters['search']:
            queryset = queryset.filter(title__icontains=filters['search'])

        # Сортировка
        ordering = filters.get('ordering')
        if ordering in ['title', '-title', 'release_date', '-release_date']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')

        # Пагинация
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return {
            "count": paginator.count,
            "results": [self._serialize_film(film) for film in page_obj.object_list]
        }

    def get_film_by_uuid(self, film_uuid: uuid.UUID) -> Optional[Dict[str, Any]]:
        try:
            film = Film.objects.prefetch_related('genres').get(uuid=film_uuid)
            return self._serialize_film(film)
        except Film.DoesNotExist:
            return None

    def create_film(self, data: Dict[str, Any]) -> Dict[str, Any]:
        genre_uuids = data.pop('genre_uuids', [])
        film = Film.objects.create(**data)
        if genre_uuids:
            genres = Genre.objects.filter(uuid__in=genre_uuids)
            film.genres.set(genres)
        return self._serialize_film(film)

    def update_film(self, film_uuid: uuid.UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        film = Film.objects.get(uuid=film_uuid)
        genre_uuids = data.pop('genre_uuids', None)
        for key, value in data.items():
            setattr(film, key, value)
        film.save()
        if genre_uuids is not None:
            genres = Genre.objects.filter(uuid__in=genre_uuids)
            film.genres.set(genres)
        return self._serialize_film(film)

    def delete_film(self, film_uuid: uuid.UUID) -> None:
        Film.objects.filter(uuid=film_uuid).delete()

    def get_genres(self) -> List[Dict[str, Any]]:
        genres = Genre.objects.all()
        return [self._serialize_genre(g) for g in genres]

    def create_genre(self, data: Dict[str, Any]) -> Dict[str, Any]:
        genre = Genre.objects.create(**data)
        return self._serialize_genre(genre)

    def update_genre(self, genre_uuid: uuid.UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        Genre.objects.filter(uuid=genre_uuid).update(**data)
        updated_genre = Genre.objects.get(uuid=genre_uuid)
        return self._serialize_genre(updated_genre)

    def delete_genre(self, genre_uuid: uuid.UUID) -> None:
        Genre.objects.filter(uuid=genre_uuid).delete()

    def get_watchlist(self, user_uuid: uuid.UUID, page: int, page_size: int) -> Dict[str, Any]:
        queryset = Watchlist.objects.filter(user_uuid=user_uuid).select_related('film').order_by('-added_at')

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        results = []
        for item in page_obj.object_list:
            results.append({
                "uuid": item.uuid,
                "film": {
                    "uuid": item.film.uuid,
                    "title": item.film.title,
                    "poster_url": item.film.poster_url,
                    "duration": item.film.duration
                },
                "added_at": item.added_at
            })

        return {
            "count": paginator.count,
            "results": results
        }

    def add_to_watchlist(self, user_uuid: uuid.UUID, film_uuid: uuid.UUID) -> Dict[str, Any]:
        film = Film.objects.get(uuid=film_uuid)
        watchlist_item, created = Watchlist.objects.get_or_create(
            user_uuid=user_uuid,
            film=film
        )
        return {
            "uuid": watchlist_item.uuid,
            "film": {
                "uuid": film.uuid,
                "title": film.title,
                "poster_url": film.poster_url
            },
            "added_at": watchlist_item.added_at
        }

    def remove_from_watchlist(self, watchlist_uuid: uuid.UUID) -> None:
        Watchlist.objects.filter(uuid=watchlist_uuid).delete()
