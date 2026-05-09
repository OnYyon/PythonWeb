import uuid
from rest_framework import status, viewsets
from rest_framework.response import Response
from ..data.repository_django import DjangoMediaRepository
from ..application.media_service import MediaServiceApp
from .serializers import (
    FilmCreateUpdateSerializer,
    GenreCreateUpdateSerializer,
    WatchlistAddSerializer,
)


class FilmViewSet(viewsets.ViewSet):
    app_service = MediaServiceApp(repository=DjangoMediaRepository())

    def list(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        filters = {
            "genre": request.query_params.get("genre"),
            "search": request.query_params.get("search"),
            "ordering": request.query_params.get("ordering"),
        }

        data = self.app_service.list_films(filters, page, page_size)
        response_data = {
            "count": data["count"],
            "next": f"/api/v1/media/film/?page={page + 1}&page_size={page_size}" if data[
                                                                                        "count"] > page * page_size else None,
            "previous": f"/api/v1/media/film/?page={page - 1}&page_size={page_size}" if page > 1 else None,
            "results": data["results"],
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk: str):
        film = self.app_service.get_film_details(uuid.UUID(pk))
        if not film:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(film, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = FilmCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        film = self.app_service.create_film(serializer.validated_data)
        return Response(film, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk: str):
        serializer = FilmCreateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        film = self.app_service.update_film(uuid.UUID(pk), serializer.validated_data)
        return Response(film, status=status.HTTP_200_OK)

    def destroy(self, request, pk: str):
        self.app_service.delete_film(uuid.UUID(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(viewsets.ViewSet):
    app_service = MediaServiceApp(repository=DjangoMediaRepository())

    def list(self, request):
        genres = self.app_service.get_all_genres()
        return Response(genres, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = GenreCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        genre = self.app_service.create_genre(serializer.validated_data)
        return Response(genre, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk: str):
        serializer = GenreCreateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        genre = self.app_service.update_genre(uuid.UUID(pk), serializer.validated_data)
        return Response(genre, status=status.HTTP_200_OK)

    def destroy(self, request, pk: str):
        self.app_service.delete_genre(uuid.UUID(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchlistViewSet(viewsets.ViewSet):
    app_service = MediaServiceApp(repository=DjangoMediaRepository())

    def _get_user_uuid(self, request) -> uuid.UUID:
        return uuid.UUID("00000000-0000-0000-0000-000000000001")

    def list(self, request):
        user_uuid = self._get_user_uuid(request)
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        data = self.app_service.get_user_watchlist(user_uuid, page, page_size)
        response_data = {
            "count": data["count"],
            "next": f"/api/v1/media/watchlist/?page={page + 1}&page_size={page_size}" if data["count"] > page *

                                                                                         page_size else None,
            "previous": f"/api/v1/media/watchlist/?page={page - 1}&page_size={page_size}" if page > 1 else None,
            "results": data["results"],
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = WatchlistAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_uuid = self._get_user_uuid(request)
        result = self.app_service.add_film_to_watchlist(user_uuid, serializer.validated_data["film_uuid"])
        return Response(result, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk: str):
        self.app_service.remove_from_watchlist(uuid.UUID(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
