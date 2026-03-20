# Yellow - AI Relationship Assistant

Production-ready монорепозиторий для Yellow, AI-ассистента для отношений.

## Структура проекта

```
yellow_assistant/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── infra/            # Docker Compose
├── Makefile          # Команды для разработки
└── README.md
```

## Технологический стек

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- pytest

### Frontend
- Next.js 14 (App Router)
- TypeScript
- React 18
- Vitest + React Testing Library

### Инфраструктура
- Docker & Docker Compose
- PostgreSQL 16

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.12+
- Node.js 20+
- Make

### Установка

1. Клонируйте репозиторий:
```bash
cd yellow_assistant
```

2. Создайте файлы окружения:

Backend (apps/api/.env):
```bash
cp apps/api/.env.example apps/api/.env
```

Frontend (apps/web/.env.local):
```bash
cp apps/web/.env.example apps/web/.env.local
```

3. Установите зависимости (для локальной разработки):
```bash
make install
```

### Запуск с Docker Compose

Запустите все сервисы (PostgreSQL, API, Web):
```bash
make up
```

Сервисы будут доступны по адресам:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

Остановить все сервисы:
```bash
make down
```

### Локальная разработка (без Docker)

#### Backend

1. Установите зависимости:
```bash
cd apps/api
pip install -r requirements.txt
```

2. Запустите PostgreSQL (или используйте Docker):
```bash
docker run -d \
  --name yellow-postgres \
  -e POSTGRES_USER=yellow \
  -e POSTGRES_PASSWORD=yellow123 \
  -e POSTGRES_DB=yellow_db \
  -p 5432:5432 \
  postgres:16-alpine
```

3. Настройте .env файл:
```bash
DATABASE_URL=postgresql://yellow:yellow123@localhost:5432/yellow_db
```

4. Запустите миграции:
```bash
alembic upgrade head
```

5. Запустите сервер:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

1. Установите зависимости:
```bash
cd apps/web
npm install
```

2. Настройте .env.local:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Запустите dev-сервер:
```bash
npm run dev
```

## Тестирование

### Запуск всех тестов
```bash
make test
```

### Backend тесты
```bash
make api-test
```

Или напрямую:
```bash
cd apps/api
pytest -v
```

### Frontend тесты
```bash
make web-test
```

Или напрямую:
```bash
cd apps/web
npm test
```

Watch mode для frontend:
```bash
cd apps/web
npm run test:watch
```

## API Endpoints

### Health Checks
- `GET /health` - Базовая проверка здоровья
- `GET /api/v1/health` - API v1 проверка здоровья

### Authentication 🔐
- `POST /api/v1/auth/register` - Регистрация нового пользователя
  - Request: `{ "email": "user@example.com", "username": "username", "password": "password123" }`
  - Response: `{ "access_token": "...", "token_type": "bearer" }`

- `POST /api/v1/auth/login` - Вход существующего пользователя
  - Request: `{ "email": "user@example.com", "password": "password123" }`
  - Response: `{ "access_token": "...", "token_type": "bearer" }`

- `GET /api/v1/auth/me` - Получить информацию о текущем пользователе (требует JWT)
  - Response: `{ "id": "uuid", "email": "...", "username": "...", "created_at": "..." }`

### Assistant (требуют JWT токен)
- `POST /api/v1/assistant/session` - Создать новую сессию
  - Response: `{ "session_id": "uuid", "status": "created" }`

- `GET /api/v1/assistant/session` - Получить или создать сессию для текущего пользователя
  - Response: `{ "session_id": "uuid", "status": "created" | "existing" }`

- `POST /api/v1/assistant/session/{session_id}/start` - Начать разговор (первый вопрос о базовой информации)
  - Response: `{ "messages": [...], "session_id": "uuid" }`
  - Первый вопрос: "Привет! Давай познакомимся 😊 Расскажи немного о себе: сколько тебе лет, твой пол и кого ты ищешь?"

- `POST /api/v1/assistant/session/{session_id}/message` - Отправить сообщение
  - Request: `{ "content": "string" }`
  - Response: `{ "user_message": {...}, "assistant_message": {...}, "profile_ready": boolean }`

- `GET /api/v1/assistant/session/{session_id}/messages` - Получить историю сообщений

### Profile (требуют JWT токен)
- `GET /api/v1/profile/{session_id}` - Получить профиль пользователя
  - Response: `{ "communication_style": "...", "attachment_style": "...", ... }`

## База данных

### Миграции

Создать новую миграцию:
```bash
cd apps/api
alembic revision --autogenerate -m "описание изменений"
```

Применить миграции:
```bash
cd apps/api
alembic upgrade head
```

Откатить миграцию:
```bash
cd apps/api
alembic downgrade -1
```

### Схема БД

**users** таблица:
- `id` (UUID, primary key)
- `email` (String, unique, indexed)
- `username` (String, unique, indexed)
- `hashed_password` (String)
- `created_at` (DateTime)

**sessions** таблица:
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key → users.id, indexed)
- `created_at` (DateTime)

**messages** таблица:
- `id` (UUID, primary key)
- `session_id` (UUID, foreign key → sessions.id)
- `role` (String: 'user' | 'assistant')
- `content` (Text)
- `created_at` (DateTime)

**profiles** таблица:
- `id` (UUID, primary key)
- `session_id` (UUID, foreign key → sessions.id, unique)
- `user_id` (UUID, foreign key → users.id, indexed)
- `age` (Integer, nullable) - возраст пользователя
- `gender` (String, nullable) - пол (male/female/non-binary/other)
- `looking_for` (String, nullable) - кого ищет (male/female/any)
- `communication_style` (Text)
- `attachment_style` (Text)
- `partner_preferences` (Text)
- `values` (Text)
- `raw_data` (JSON)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Makefile команды

```bash
make up              # Запустить все сервисы в Docker
make down            # Остановить все сервисы
make api-test        # Запустить backend тесты
make web-test        # Запустить frontend тесты
make test            # Запустить все тесты
make install         # Установить все зависимости
make install-api     # Установить backend зависимости
make install-web     # Установить frontend зависимости
make migrate         # Применить миграции БД
make logs            # Показать логи Docker
make restart         # Перезапустить все сервисы
make clean           # Очистить всё (включая volumes)
```

## Архитектура

### Backend

```
apps/api/
├── alembic/              # Миграции БД
├── app/
│   ├── main.py          # FastAPI приложение
│   ├── config.py        # Настройки
│   ├── database.py      # Подключение к БД
│   ├── models/          # SQLAlchemy модели
│   ├── routers/         # API endpoints
│   ├── schemas/         # Pydantic схемы
│   └── services/        # Бизнес-логика
└── tests/               # Тесты
```

### Frontend

```
apps/web/
├── src/
│   ├── app/             # Next.js App Router
│   ├── components/      # React компоненты
│   └── lib/             # Утилиты (API client)
└── tests/               # Тесты
```

## Разработка

### Добавление новых зависимостей

Backend:
```bash
cd apps/api
pip install <package>
pip freeze > requirements.txt
```

Frontend:
```bash
cd apps/web
npm install <package>
```

### Стиль кода

Backend:
- Type hints везде
- Dependency injection для DB session
- Разделение на layers: routers → services → models

Frontend:
- TypeScript strict mode
- Функциональные компоненты
- Простой API client wrapper

## Troubleshooting

### Порты заняты
Если порты 3000, 8000 или 5432 заняты, остановите конфликтующие сервисы или измените порты в docker-compose.yml.

### База данных не подключается
Убедитесь, что PostgreSQL запущен и доступен:
```bash
docker-compose -f infra/docker-compose.yml ps
```

### Тесты падают
Убедитесь, что все зависимости установлены:
```bash
make install
```

## Прогресс разработки

- ✅ **Step 1**: Базовая инфраструктура (FastAPI, Next.js, PostgreSQL, Docker)
- ✅ **Step 2**: Чат с AI профилированием
- ✅ **Step 2.1**: Вход и восстановление истории
- ✅ **Step 2.2**: Аутентификация с паролем и JWT
- ✅ **Step 3**: Система матчинга (до 5 совпадений в день)
- ⏳ **Step 4**: Чат с реальными людьми
- ⏳ **Step 5**: Бронирование событий

См. `STEP2.md` для деталей Step 2.
См. `STEP2_LOGIN.md` для деталей входа и восстановления истории.
См. `AUTHENTICATION.md` для деталей аутентификации с паролем.
См. `STEP3.md` для деталей системы матчинга.

## Основные возможности

### 🔐 Аутентификация
- **Регистрация**: Email, username, пароль (минимум 8 символов)
- **Вход**: Email и пароль
- **JWT токены**: Срок действия 7 дней
- **Auto-login**: Токен сохраняется в localStorage
- **Безопасность**: Пароли хешируются через bcrypt

### 💬 Чат с AI
- **Первый вопрос**: AI просит представиться (возраст, пол, кого ищешь)
- AI автоматически извлекает базовую информацию из ответа
- AI задаёт уточняющие вопросы по одному
- Вся история сохраняется в базе данных

### 👤 Профиль пользователя
- После 5 ответов AI создаёт структурированный профиль
- Профиль включает:
  - **Базовую информацию**: возраст, пол, кого ищет (извлекается из первого ответа)
  - Стиль общения
  - Тип привязанности
  - Предпочтения в партнёре
  - Ценности
- Профиль отображается в правой панели

### 💕 Система матчинга
- До 5 совпадений в день
- **Gender filtering**: показывает только тех, кто соответствует вашим предпочтениям
- Простой алгоритм на основе схожести профилей
- Оценка совместимости (0-100%)
- Отображение возраста рядом с именем
- Объяснение почему вы подходите
- Кнопка "Start Chat" (placeholder)

### 📜 Восстановление истории
- Вся история чата сохраняется
- При повторном входе история автоматически восстанавливается
- Можно выйти и войти под другим аккаунтом

## Статистика

**Backend:** 41 тест ✅ (включая 10 тестов матчинга)
**Frontend:** 36 тестов ✅ (включая 10 тестов matches)
**Total:** 77 тестов ✅

## Лицензия

Proprietary
