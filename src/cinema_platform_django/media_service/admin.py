from django.contrib import admin

from src.cinema_platform_django.media_service.infrastructure.models.media import (
    Film,
    Genre,
    Watchlist,
)

admin.register(Film)
admin.register(Genre)
admin.register(Watchlist)
