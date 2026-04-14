migrate:
	uv run src/cinema_platform_django/manage.py migrate

lint:
	uv run ty check .
	uv run ruff check .

test:
	uv run src/cinema_platform_django/manage.py test

run:
	uv run src/cinema_platform_django/manage.py runserver
