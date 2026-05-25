import os
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name: str) -> str:
    try:
        return os.environ[var_name]
    except KeyError:
        raise ImproperlyConfigured(f"Environment variable {var_name} is missing.")


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env_variable("DB_NAME"),
        "USER": get_env_variable("DB_USER"),
        "PASSWORD": get_env_variable("DB_PASSWORD"),
        "HOST": get_env_variable("DB_HOST"),
        "PORT": int(os.environ.get("DB_PORT", 5432)),
        "OPTIONS": {"options": "-c search_path=public,content"},
    }
}
