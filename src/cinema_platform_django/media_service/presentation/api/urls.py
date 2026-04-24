from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FilmViewSet, GenreViewSet, WatchlistViewSet


router = DefaultRouter()
router.register(r"film", FilmViewSet, basename="film")
router.register(r"genre", GenreViewSet, basename="genre")
router.register(r"watchlist", WatchlistViewSet, basename="watchlist")

urlpatterns = [
    path("", include(router.urls)),
]
