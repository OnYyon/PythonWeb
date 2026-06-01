# Recommendation Service

сервис для получения рекомендаций фильмов на основе истории просмотра пользователя.

## Описание

Сервис анализирует фильмы, которые смотрел пользователь, определяет его любимые жанры и рекомендует похожие фильмы. Если пользователь новый (нет истории просмотра), возвращаются самые новые фильмы.

## Запуск

### Требования
- Python 3.10+
- PostgreSQL 12+
- Virtual Environment

### Установка зависимостей

```bash
cd /Users/pavel/Documents/GitHub/PythonWeb
pip install -r requirements.txt
```

### Запуск сервиса

Из корня проекта:

```bash
source .venv/bin/activate
python3 src/recommendation_service/run.py [PORT]
```

Если PORT не указан, используется порт **5002** по умолчанию.


## API Endpoints

### GET /api/v1/recommendations

Получить список рекомендованных фильмов для пользователя.

#### Заголовки (Headers)
```
X-User-Id: [UUID или строка ID пользователя] (обязателен)
```

#### Параметры запроса
Нет параметров URL. ID пользователя передаётся через заголовок `X-User-Id`.



## Структура проекта

```
recommendation_service/
├── __init__.py           # Экспорт create_app
├── run.py               # Точка входа приложения
├── README.md            # Документация
└── app/
    ├── __init__.py      # Инициализация Flask приложения
    ├── database.py      # Конфигурация SQLAlchemy
    ├── models.py        # ORM модели (Film, Genre, Watchlist)
    ├── routes.py        # API endpoints
    └── service.py       # Бизнес-логика рекомендаций
```


## Модели данных

### Film
- `uuid` (UUID): уникальный идентификатор
- `title` (String): название фильма
- `description` (Text): описание
- `release_date` (Date): дата выхода
- `duration` (Integer): длительность в минутах
- `poster_url` (String): URL постера
- `created_at` (DateTime): дата создания записи
- `updated_at` (DateTime): дата последнего обновления

### Genre
- `uuid` (UUID): уникальный идентификатор
- `name` (String): название жанра
- `description` (Text): описание жанра

### Watchlist
- `uuid` (UUID): уникальный идентификатор
- `user_uuid` (UUID): ID пользователя
- `film_id` (UUID): ID фильма (внешний ключ)
- `added_at` (DateTime): дата добавления в watchlist

## Примеры использования

### cURL

```bash
curl -X GET http://127.0.0.1:5001/api/v1/recommendations/ \
  -H "X-User-Id: user-123"
```

## Проверки кода

### Lint проверки (Ruff)

Проверить код на соответствие стандартам:

```bash
cd /Users/pavel/Documents/GitHub/PythonWeb
. .venv/bin/activate
ruff check src/recommendation_service/
```

Автоматически исправить проблемы:

```bash
ruff check src/recommendation_service/ --fix
```

### Type checking (MyPy)

```bash
mypy src/recommendation_service/ --ignore-missing-imports
```

### Syntax проверка

```bash
python3 -m py_compile src/recommendation_service/**/*.py
```

### Все проверки вместе

```bash
. .venv/bin/activate
ruff check src/recommendation_service/
python3 -m py_compile src/recommendation_service/**/*.py
python3 -c "import sys; sys.path.insert(0, 'src'); from recommendation_service import create_app; print('✅ All checks passed!')"
```
