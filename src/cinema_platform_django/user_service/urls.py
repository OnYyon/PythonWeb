from django.urls import path
from .views import user_collection_view, user_detail_media_view

urlpatterns = [
    path("user/", user_collection_view, name="user-collection"),
    path("media/user/<uuid:user_id>/", user_detail_media_view, name="user-detail-media"),
]
