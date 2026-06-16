from django.contrib import admin
from ..data.models import Film, Genre, Watchlist

admin.register(Film)
admin.register(Genre)
admin.register(Watchlist)
