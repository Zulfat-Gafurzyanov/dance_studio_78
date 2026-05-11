# Dance Studio 78

Веб-приложение для танцевальной студии «Семь-Восемь» (Казань). Публичная часть — лендинг со стилями, преподавателями и ценами. Административная часть — управление контентом через защищённую панель.

## Стек

| Слой | Технологии |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, asyncpg, Alembic |
| Auth | JWT RS256, Argon2, Redis (refresh-токены) |
| Frontend | HTML5, CSS3, Vanilla JS (ES-модули) |
| Инфраструктура | Docker Compose, Nginx, PostgreSQL 16, Redis 7 |

## Как это работает

1. Nginx принимает запросы на порту 8080 и раздаёт статику фронтенда
2. Запросы на `/api/` проксируются к FastAPI-бэкенду (порт 8000)
3. Бэкенд хранит данные в PostgreSQL и использует Redis для JWT refresh-токенов
4. Аутентификация — JWT (RS256): access-токен 1 час, refresh-токен 7 дней
5. При 401 фронтенд автоматически обновляет токен и повторяет запрос

## Требования

- Docker и Docker Compose
- OpenSSL (для генерации RSA-ключей)

## Установка

```bash
git clone <repo>
cd dance_studio_78

# Скопировать шаблоны переменных окружения
cp .env.example .env
cp backend/.env.example backend/.env

# Сгенерировать RSA-ключи для JWT
mkdir -p backend/keys
openssl genrsa -out backend/keys/private.pem 2048
openssl rsa -in backend/keys/private.pem -pubout -out backend/keys/public.pem
```

## Настройка

В проекте два env-файла для двух разных потребителей.

### `.env` (корень проекта)

Читается Docker Compose при подстановке переменных в `docker-compose.yml`. Используется только для инициализации контейнера PostgreSQL.

| Переменная | Пример | Описание |
|---|---|---|
| `POSTGRES_USER` | `postgres` | Пользователь БД |
| `POSTGRES_PASSWORD` | `changeme` | Пароль БД |
| `POSTGRES_DB` | `dance_studio` | Имя базы данных |

### `backend/.env`

Передаётся внутрь контейнера бэкенда через `env_file:` и читается FastAPI-приложением.

| Переменная | Пример | Описание |
|---|---|---|
| `APP_NAME` | `78 Dance` | Название приложения |
| `DEBUG` | `false` | Режим отладки |
| `DATABASE_URL` | `postgresql://postgres:changeme@postgres:5432/dance_studio` | Строка подключения к БД |
| `DATABASE_URL_SQLALCHEMY` | `postgresql+asyncpg://...` | То же, для SQLAlchemy |
| `REDIS_URL` | `redis://redis:6379/0` | Строка подключения к Redis |
| `CORS_ORIGINS` | `["http://localhost:8080"]` | Разрешённые CORS-источники (JSON-массив) |
| `JWT_PRIVATE_KEY_PATH` | `keys/private.pem` | Путь к приватному ключу |
| `JWT_PUBLIC_KEY_PATH` | `keys/public.pem` | Путь к публичному ключу |
| `ACCESS_TOKEN_LIFETIME` | `3600` | Время жизни access-токена (секунды) |
| `REFRESH_TOKEN_LIFETIME` | `604800` | Время жизни refresh-токена (секунды) |

> Учётные данные PostgreSQL указываются в обоих файлах — при смене пароля обновляй оба.

## Запуск

```bash
# Собрать и запустить все сервисы
docker-compose up --build

# Фоновый режим
docker-compose up -d --build

# Остановить
docker-compose down
```

После запуска:

| Адрес | Что открывается |
|---|---|
| `http://localhost:8080` | Публичный лендинг |
| `http://localhost:8080/auth` | Страница входа / регистрации |
| `http://localhost:8080/admin/` | Административная панель |
| `http://localhost:8080/api/v1/health` | Проверка состояния сервисов |

Бэкенд при старте автоматически применяет миграции Alembic (`alembic upgrade head`), затем поднимает Gunicorn с 4 Uvicorn-воркерами.

## API

Базовый путь: `/api/v1`

### Аутентификация

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/auth/sign-up` | Регистрация |
| `POST` | `/auth/sign-in` | Вход |
| `POST` | `/auth/refresh` | Обновление токена |

### Пользователи

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/users/me` | Получить профиль |
| `PATCH` | `/users/me` | Обновить профиль |
| `DELETE` | `/users/me` | Удалить аккаунт |

### Контент (требует роль `admin`)

| Метод | Путь | Описание |
|---|---|---|
| `GET / POST / PATCH / DELETE` | `/styles`, `/teachers`, `/prices` | CRUD для стилей, преподавателей, прайсов |
| `POST` | `/teachers/reorder` | Изменить порядок преподавателей |
| `GET / PATCH` | `/studioinfo` | Информация о студии |
| `GET / PATCH / DELETE` | `/admin/users/{id}/role` | Управление ролями пользователей |

### Пример ответа `/health`

```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok"
}
```

## Тесты

Тесты не ходят в сеть — база и Redis подменяются фикстурами. Запуск из папки `backend/`:

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

Запуск с отчётом о покрытии:

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

**Покрытие: 83%**

### Что покрыто

| Файл | Тестов | Содержание |
|---|---|---|
| `tests/test_auth.py` | 7 | Регистрация, вход, несовпадение паролей, дубль email (409), неверный пароль (401), заблокированный аккаунт (403) |
| `tests/test_health.py` | 3 | `/health` в норме, при падении БД, при падении Redis |
| `tests/test_users.py` | 6 | Профиль: чтение, обновление email и пароля, удаление аккаунта; 401 без токена и для деактивированных |
| `tests/test_admin.py` | 7 | Список пользователей с пагинацией, поиск по id, смена роли и флага активности; 403 для не-admin |
| `tests/test_style.py` | 14 | CRUD стилей + добавление / обновление / удаление изображений; happy path и 404 |
| `tests/test_teacher.py` | 15 | CRUD преподавателей + фото + изменение порядка (`reorder`); happy path и 404 |
| `tests/test_price.py` | 14 | CRUD тарифных планов + опции плана; happy path, 404 и 401 без токена |
| `tests/test_studioinfo.py` | 5 | Чтение (200/404) и обновление одного / нескольких полей; 401 без токена |
| **Итого** | **71** | |

| Вспомогательный файл | Назначение |
|---|---|
| `tests/conftest.py` | Фикстуры: тестовый клиент, моки соединения с БД и Redis |
| `tests/helpers.py` | Общие тестовые строки (строки БД, генераторы JWT для user / admin) |

## Структура проекта

```
dance_studio_78/
├── backend/
│   ├── entrypoint.sh           # миграции → gunicorn
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pg/migrations/          # Alembic-миграции
│   ├── .env.example            # приложение, Redis, JWT
│   ├── main.py                 # точка входа, инициализация FastAPI, lifespan
│   └── src/
│       ├── api/v1/             # маршруты: auth, users, admin, styles, teachers, prices, studioinfo
│       ├── core/               # config, constants, security (JWT, Argon2)
│       ├── db/                 # пул asyncpg, декларативная база SQLAlchemy
│       ├── middleware/         # логирование запросов
│       ├── models/             # SQLAlchemy-модели: User, Teacher, Style, Price, StudioInfo
│       ├── repository/         # слой доступа к данным (CRUD над моделями)
│       ├── schemas/            # Pydantic-схемы запросов и ответов
│       ├── service/            # бизнес-логика (вызывает repository)
│       └── utils/              # вспомогательные утилиты (настройка логгера)
├── frontend/
│   ├── index.html              # публичный лендинг
│   ├── auth.html               # вход / регистрация
│   ├── admin/                  # страницы панели управления
│   ├── errors/                 # кастомные страницы ошибок
│   ├── css/                    # стили
│   └── js/
│       ├── api.js              # API-клиент с автообновлением токена
│       └── utils.js            # работа с токенами, UI-хелперы
├── nginx/
│   └── nginx.conf              # проксирование /api/, раздача статики, security-заголовки
│
├── docker-compose.yml          # postgres, redis, backend, nginx
└── .env.example                # учётные данные PostgreSQL
```

## Первый администратор

После первого запуска в базе нет ни одного admin-пользователя. Порядок действий:

1. Зарегистрируйся через `/auth/sign-up` или страницу `/auth`
2. Повысь пользователя до admin напрямую в БД:

```bash
docker-compose exec postgres psql -U postgres -d dance_studio -c \
  "UPDATE \"user\" SET role = 'admin' WHERE email = 'your@email.com';"
```

3. После этого в `/admin/` станут доступны управление пользователями, преподавателями, стилями и ценами. Все последующие повышения можно делать через интерфейс панели.

## Ограничения

- RSA-ключи нужно генерировать вручную перед первым запуском
- Refresh-токены одноразовые — при параллельном обновлении из двух вкладок один из запросов получит 401
- Загружаемые фото хранятся внутри контейнера; при пересоздании тома они теряются — для продакшена нужно монтировать внешний volume или использовать S3