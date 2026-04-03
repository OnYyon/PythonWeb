import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(unique=True, max_length=254)),
                ("username", models.CharField(unique=True, max_length=150)),
                ("password_hash", models.CharField(max_length=255)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("user", "User"),
                        ],
                        default="user",
                        max_length=20,
                    ),
                ),
                ("full_name", models.CharField(max_length=255, blank=True)),
                (
                    "phone",
                    models.CharField(max_length=20, unique=True, null=True, blank=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "users"},
        ),
    ]
