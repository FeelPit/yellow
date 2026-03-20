# Yellow - Команды для запуска Step 2

## Быстрый старт (все в одном)

```bash
# 1. Установить зависимости
cd apps/api
source venv/bin/activate
pip install -r requirements.txt

cd ../web
npm install

# 2. Настроить .env файлы
cd ../api
cp .env.example .env
# Отредактируйте .env и добавьте ваш OPENAI_API_KEY

cd ../web
cp .env.example .env.local

# 3. Применить миграции (локально)
cd ../api
source venv/bin/activate
export DATABASE_URL="postgresql://yellow:yellow123@localhost:5432/yellow_db"
alembic upgrade head

# 4. Запустить с Docker
cd ../..
make up

# 5. Открыть приложение
# Frontend: http://localhost:3000/assistant
# API Docs: http://localhost:8000/docs
```

## Пошаговые команды

### 1. Обновить backend зависимости

```bash
cd apps/api
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Обновить frontend зависимости

```bash
cd apps/web
npm install
```

### 3. Настроить переменные окружения

**Backend:**
```bash
cd apps/api
cp .env.example .env

# Отредактируйте .env:
# OPENAI_API_KEY=your-actual-key-here
# OPENAI_MODEL=gpt-4o-mini
```

**Frontend:**
```bash
cd apps/web
cp .env.example .env.local

# Должно быть:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Применить миграции БД

**С Docker (рекомендуется):**
```bash
# Запустите Docker Compose
make up

# Миграции применятся автоматически при старте API контейнера
```

**Локально (без Docker):**
```bash
# Сначала запустите PostgreSQL
docker run -d \
  --name yellow-postgres \
  -e POSTGRES_USER=yellow \
  -e POSTGRES_PASSWORD=yellow123 \
  -e POSTGRES_DB=yellow_db \
  -p 5432:5432 \
  postgres:16-alpine

# Затем примените миграции
cd apps/api
source venv/bin/activate
export DATABASE_URL="postgresql://yellow:yellow123@localhost:5432/yellow_db"
alembic upgrade head
```

### 5. Запустить приложение

**С Docker (рекомендуется):**
```bash
make up
```

**Локально:**

Terminal 1 - Backend:
```bash
cd apps/api
source venv/bin/activate
uvicorn app.main:app --reload
```

Terminal 2 - Frontend:
```bash
cd apps/web
npm run dev
```

### 6. Открыть приложение

- Frontend: http://localhost:3000
- Assistant Page: http://localhost:3000/assistant
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

## Тестирование

### Все тесты

```bash
make test
```

### Backend тесты (19 тестов)

```bash
cd apps/api
source venv/bin/activate
pytest -v

# Конкретные файлы
pytest tests/test_messages.py -v
pytest tests/test_profile.py -v

# С покрытием
pytest --cov=app tests/
```

### Frontend тесты (20 тестов)

```bash
cd apps/web
npm test

# Watch mode
npm run test:watch

# Конкретные файлы
npm test tests/components/ChatMessage.test.tsx
```

## Проверка работы API

### Health checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

### Создать сессию

```bash
curl -X POST http://localhost:8000/api/v1/assistant/session \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user"}'

# Ответ:
# {"session_id":"uuid-here","status":"created"}
```

### Начать разговор

```bash
# Используйте session_id из предыдущего шага
SESSION_ID="your-session-id-here"

curl -X POST http://localhost:8000/api/v1/assistant/session/$SESSION_ID/start

# Ответ: 3 вопроса от AI
```

### Отправить сообщение

```bash
curl -X POST http://localhost:8000/api/v1/assistant/session/$SESSION_ID/message \
  -H "Content-Type: application/json" \
  -d '{"content":"I am looking for a meaningful relationship"}'

# Ответ: user_message, assistant_message, profile_ready
```

### Получить историю

```bash
curl http://localhost:8000/api/v1/assistant/session/$SESSION_ID/messages
```

### Получить профиль (после 5 сообщений)

```bash
curl http://localhost:8000/api/v1/profile/$SESSION_ID
```

## Управление Docker

```bash
# Запустить все сервисы
make up

# Остановить все сервисы
make down

# Перезапустить
make restart

# Посмотреть логи
make logs

# Посмотреть логи конкретного сервиса
cd infra && docker-compose logs -f api
cd infra && docker-compose logs -f web

# Очистить всё (включая volumes)
make clean
```

## Управление миграциями

### Применить миграции

```bash
cd apps/api
source venv/bin/activate
alembic upgrade head
```

### Откатить миграцию

```bash
alembic downgrade -1
```

### Создать новую миграцию

```bash
alembic revision --autogenerate -m "описание изменений"
```

### Посмотреть текущую версию

```bash
alembic current
```

### История миграций

```bash
alembic history
```

## Troubleshooting

### OpenAI API не работает

```bash
# Проверьте ключ
echo $OPENAI_API_KEY

# Проверьте в .env файле
cat apps/api/.env | grep OPENAI

# Тесты всегда используют mock, не требуют реальный ключ
```

### Порты заняты

```bash
# Проверьте что занимает порты
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Остановите конфликтующие процессы
make down
```

### База данных не подключается

```bash
# Проверьте статус контейнеров
cd infra && docker-compose ps

# Перезапустите PostgreSQL
make down
make up
```

### Миграции не применяются

```bash
# Проверьте текущую версию
cd apps/api
source venv/bin/activate
alembic current

# Примените все миграции
alembic upgrade head

# Если есть ошибки, посмотрите логи
cd ../.. && make logs
```

### Тесты падают

```bash
# Backend: убедитесь что venv активирован
cd apps/api
source venv/bin/activate
pytest -v

# Frontend: очистите кэш
cd apps/web
rm -rf node_modules/.vite
npm test
```

## Полезные команды

```bash
# Посмотреть структуру БД
cd apps/api
source venv/bin/activate
python -c "from app.database import engine; from app.models import *; print(Base.metadata.tables.keys())"

# Подключиться к PostgreSQL
docker exec -it infra-postgres-1 psql -U yellow -d yellow_db

# Посмотреть таблицы
\dt

# Посмотреть данные
SELECT * FROM sessions;
SELECT * FROM messages;
SELECT * FROM profiles;

# Выйти
\q
```

## Статус тестов

✅ Backend: 19/19 тестов проходят
✅ Frontend: 20/20 тестов проходят
✅ Все критические пути покрыты
✅ OpenAI всегда мокается в тестах
