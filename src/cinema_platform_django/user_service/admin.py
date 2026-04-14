from django.contrib import admin

from src.cinema_platform_django.user_service.infrastructure.models.user import (
    User,
)

admin.site.register(User)
