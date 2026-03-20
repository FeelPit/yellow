# Yellow - Быстрый старт

## Что создано в Step 1

✅ Production-ready монорепозиторий с:
- FastAPI backend с PostgreSQL
- Next.js frontend
- Docker Compose для локальной разработки
- Полное покрытие автоматическими тестами
- Alembic миграции
- Makefile для удобства

## Быстрый запуск (Docker)

```bash
# 1. Запустить все сервисы
make up

# 2. Открыть в браузере
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# API: http://localhost:8000

# 3. Остановить
make down
```

## Проверка работы

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API v1 health
curl http://localhost:8000/api/v1/health

# Создать сессию
curl -X POST http://localhost:8000/api/v1/assistant/session \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user"}'
```

### Frontend

Откройте http://localhost:3000 в браузере:
- Главная страница с кнопкой "Начать"
- Страница /assistant с кнопкой "Начать сессию"
- При клике создается сессия через API и отображается session_id

## Тесты

```bash
# Все тесты
make test

# Только backend
make api-test

# Только frontend
make web-test
```

## Локальная разработка (без Docker)

### Backend

```bash
cd apps/api

# Создать venv и установить зависимости
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запустить PostgreSQL
docker run -d \
  --name yellow-postgres \
  -e POSTGRES_USER=yellow \
  -e POSTGRES_PASSWORD=yellow123 \
  -e POSTGRES_DB=yellow_db \
  -p 5432:5432 \
  postgres:16-alpine

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

### Frontend

```bash
cd apps/web

# Установить зависимости
npm install

# Запустить dev сервер
npm run dev
```

## Структура БД

**sessions** таблица:
- `id` (UUID, primary key)
- `user_id` (String, indexed)
- `created_at` (DateTime)

## Технологии

**Backend:**
- Python 3.12
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Alembic 1.13.1
- PostgreSQL 16
- pytest

**Frontend:**
- Next.js 14.1.0
- React 18
- TypeScript
- Vitest
- React Testing Library

## Следующие шаги

Step 1 завершен. Готов к следующим этапам:
- Профиль пользователя
- AI рекомендации
- Чат
- События
