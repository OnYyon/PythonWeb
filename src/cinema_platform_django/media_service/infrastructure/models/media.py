import uuid
from django.db import models


class Genre(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "genres"

    def __str__(self):
        return self.name


class Film(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    release_date = models.DateField()
    duration = models.IntegerField()
    poster_url = models.URLField(max_length=500, null=True, blank=True)

    genres = models.ManyToManyField(Genre, related_name="films", db_table="film_genres")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "films"

    def __str__(self):
        return self.title


class Watchlist(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_uuid = models.UUIDField()
    film = models.ForeignKey(
        Film, on_delete=models.CASCADE, related_name="in_watchlists"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "watchlist"
        unique_together = ("user_uuid", "film")

    def __str__(self):
        return f"User {self.user_uuid} - Film {self.film.title}"
