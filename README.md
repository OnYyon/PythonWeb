# Проект

## Спринты

### 1 спринт
- написание каркасных приложений для django(subscription, user, films(находиться в другой ветке PR-33) services)
- обговаривание флоу разрабокти
- настройка репо(ci, branch ruleset, project, wiki, depandabot, security and quality)

### 2 спринт
- передлелования под "чистую архитектуру" django сервисов
- настройка логера

### 3 спринт
- сервис авторизации, платежный, нотификации(на момент коммита не было)

### 4 спринт
- серивис рекомендаций(flask), хранения коментов, оценок и тд(на момент коммита не было)

## Бытсрый старт

Просто выполните комаду:

```bash
docker compose up -d
```

Поднимуться сервисы:
- auth
- payment
- django(все приложения django)
- recommendation

## Доки
Есть страники на вики с доками

## Конфигурация приложения
Все нужные env проставленны в docker compose файле. Но так же можно их задаовать через .env
В env.example привед пример.

## Полезыне ссылки
```text
https://www.postman.com/okyyok/workspace/python-web/request/42759148-e65d448f-7210-4421-be9b-57fba8f64275?action=share&creator=42759148&active-environment=42759148-4ad27854-0c40-4736-b4ea-cbf46aafa77f
```
Это моя(Kim Oleg) собственная коллеция в которой я проводил в основном тесты своих сервисов.
Там есть мини-скрипты которые автоматом заплоняют env и подставляеються во все нужные места, нужно соблюдать лишь порядок действий

## Флоу

### Чтобы затронуть subscrption и payment сервис
1) Создать пользователя.

  Пример запроса на `POST api/v1/user/`
  ```bash
  curl --location 'http://localhost:80/api/v1/user/' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "username": "zxcurseddd",
    "email": "zov@example.comnm",
    "password": "StrongPass123!",
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "phone": "+7993912345677",
    "role": "admin"
  }'
  ```
2) Войти под ним

  Пример запроса на `POST /api/v1/auth/login/`
  ```bash
  curl --location 'http://localhost:80/api/v1/auth/login' \
  --header 'X-User-Id: null' \
  --header 'Content-Type: application/json' \
  --data '{
      "username": "zxcurseddd",
      "password": "StrongPass123!"
  }'
  ```

3) Создать карту для польза

  Пример запроса на `POST /api/v1/cards/`
  ```bash
  curl --location 'http://localhost:80/api/v1/cards' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer {{access_token}}' \
  --data '{
      "initial_balance": 1000.0
  }'
  ```

4) Создать план(подразумеваеться что может быть несколько планов для подписок)

  Пример запроса на `POST /api/v1/admin/plans/`
  ```bash
  curl --location 'http://localhost:80/api/v1/admin/plans/' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer {{access_token}}' \
  --data '{
      "name": "Base",
      "price": 100.00,
      "duration": 1
  }
  '
  ```

5) Создать подписку для польза(активная может быть только 1)

  Пример запроса на `POST /api/v1/subscriptions/`
  ```bash
  curl --location 'http://localhost:80/api/v1/subscriptions/' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer {{access_token}}' \
  --data '{
      "plan_id": "{{plan_id}}",
      "auto_renew": true
  }
  '
  ```

6) Активировать подписку

 Пример запроса на `POST /api/v1/subscriptions/me/activate/`
  ```bash
  curl --location 'http://localhost:80/api/v1/subscriptions/me/activate/' \
  --header 'X-User-Id: null' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer {{access_token}}' \
  --data '{
      "card_id": "{{card_id}}"
  }'
  ```

Итог вы создали пользоветеля, создали для него карту и оплатили подписку, план который вы тоже создали


### Флоу для сервиса рекомендаций
- Endpoint: GET /api/v1/recommendations
  - Авторизация: Authorization: Bearer <JWT> (в payload должен быть sub; user_id поддерживается как fallback)
  - Успешный ответ: 200 JSON массив фильмов; поля: id, title, description, release_date (ISO), duration, poster_url, genres: [{id, name}]
  - Ошибки: 401 при отсутствии/некорректном токене, 400 при неверном форматe user_id, 500 при внутренней ошибке

Поведение:
- Если у пользователя нет записей в watchlist → возвращаются 10 новейших фильмов
- Иначе → подбираются до 10 фильмов по любимым жанрам пользователя, исключая уже просмотренные
- Если рекомендаций по жанрам нет → fallback: 10 новейших фильмов, исключая просмотренные

Пример запроса:
```bash
curl -s 'http://localhost:5001/api/v1/recommendations' \
  -H 'Authorization: Bearer {{access_token}}'
```

Примечание: сервис получает id пользователя из JWT; параметр user_id в query не используется.

Примеры ответов:

- 200 OK — успешный ответ (массив фильмов):
```json
[
  {
    "id": "111e4567-e89b-12d3-a456-426614174000",
    "title": "Example Film",
    "description": "Короткое описание",
    "release_date": "2025-12-01",
    "duration": 120,
    "poster_url": "http://example.com/poster.jpg",
    "genres": [{"id": "222e4567-e89b-12d3-a456-426614174000", "name": "Drama"}]
  }
]
```

- 401 Unauthorized — отсутствие или некорректный Bearer токен:
```json
{"error": "Unauthorized"}
```
или
```json
{"error": "Invalid or expired token"}
```

- 400 Bad Request — неверный формат user_id в payload токена:
```json
{"error": "Invalid User ID format"}
```

- 500 Internal Server Error — внутренняя ошибка сервиса:
```json
{"error": "Internal server error"}
```

(Если в БД нет фильмов/данных — успешный 200 может вернуть пустой массив `[]`.)
