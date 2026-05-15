from rest_framework import serializers


class GenreResponseSerializer(serializers.Serializer):
    """Сериализатор для отдачи жанра"""

    uuid = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True, required=False)


class GenreCreateUpdateSerializer(serializers.Serializer):
    """Сериализатор для валидации при создании или обновлении жанра"""

    name = serializers.CharField(max_length=100)
    description = serializers.CharField(
        allow_blank=True, required=False, allow_null=True
    )


class FilmResponseSerializer(serializers.Serializer):
    """Сериализатор для отдачи фильма"""

    uuid = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    release_date = serializers.DateField()
    duration = serializers.IntegerField()
    poster_url = serializers.URLField(allow_null=True)
    genres = GenreResponseSerializer(many=True)


class FilmCreateUpdateSerializer(serializers.Serializer):
    """Сериализатор для валидации при создании или обновлении фильма"""

    title = serializers.CharField(max_length=255)
    description = serializers.CharField(
        allow_blank=True, required=False, allow_null=True
    )
    release_date = serializers.DateField()
    duration = serializers.IntegerField(min_value=1)
    poster_url = serializers.URLField(allow_blank=True, required=False, allow_null=True)
    genre_uuids = serializers.ListField(child=serializers.UUIDField(), required=False)


class WatchlistFilmSerializer(serializers.Serializer):
    """Укороченная версия фильма для списка просмотра"""

    uuid = serializers.UUIDField()
    title = serializers.CharField()
    poster_url = serializers.URLField(allow_null=True)
    duration = serializers.IntegerField(required=False)


class WatchlistResponseSerializer(serializers.Serializer):
    """Сериализатор для отдачи записи из watchlist"""

    uuid = serializers.UUIDField()
    film = WatchlistFilmSerializer()
    added_at = serializers.DateTimeField()


class WatchlistAddSerializer(serializers.Serializer):
    """Сериализатор для валидации при добавлении в watchlist"""

    film_uuid = serializers.UUIDField()
