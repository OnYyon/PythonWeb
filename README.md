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
