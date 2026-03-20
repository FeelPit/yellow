# Yellow - Step 2: Chat & Profile

## Что добавлено в Step 2

✅ **Backend:**
- Полноценный чат с OpenAI интеграцией
- POST `/api/v1/assistant/session/{id}/start` - начать разговор (3 вопроса)
- POST `/api/v1/assistant/session/{id}/message` - отправить сообщение
- GET `/api/v1/assistant/session/{id}/messages` - история сообщений
- GET `/api/v1/profile/{session_id}` - получить профиль
- Автоматическое создание профиля после 5 сообщений
- Таблицы: messages, profiles
- OpenAI mock для тестов (реальный API не вызывается)

✅ **Frontend:**
- Полноценный chat UI с пузырьками сообщений
- Автоматическая инициализация сессии
- Отправка сообщений и получение ответов
- Статус профиля: "Узнаём о вас..." → "Профиль готов"
- Панель профиля справа с 4 секциями
- Все компоненты покрыты тестами

✅ **Тесты:**
- 18 backend тестов (все проходят)
- 11 frontend тестов (все проходят)
- OpenAI всегда мокается в тестах

## Быстрый старт

### 1. Обновить зависимости

```bash
# Backend
cd apps/api
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd apps/web
npm install
```

### 2. Настроить переменные окружения

**Backend (.env):**
```bash
cd apps/api
cp .env.example .env

# Отредактируйте .env:
OPENAI_API_KEY=your-actual-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

**Frontend (.env.local):**
```bash
cd apps/web
cp .env.example .env.local

# Должно быть:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Применить миграции

```bash
cd apps/api
source venv/bin/activate
alembic upgrade head
```

### 4. Запустить с Docker

```bash
# Из корня проекта
make down  # Остановить старые контейнеры
make up    # Запустить все сервисы
```

### 5. Открыть приложение

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Перейдите на http://localhost:3000/assistant

## Локальная разработка (без Docker)

### Backend

```bash
cd apps/api
source venv/bin/activate

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

### Frontend

```bash
cd apps/web
npm run dev
```

## Тестирование

### Все тесты

```bash
make test
```

### Backend тесты

```bash
cd apps/api
source venv/bin/activate
pytest -v

# Конкретные тесты
pytest tests/test_messages.py -v
pytest tests/test_profile.py -v
```

### Frontend тесты

```bash
cd apps/web
npm test

# Watch mode
npm run test:watch
```

## API Endpoints (новые)

### Начать разговор

```bash
POST /api/v1/assistant/session/{session_id}/start

Response:
{
  "messages": [
    {
      "id": "uuid",
      "session_id": "uuid",
      "role": "assistant",
      "content": "Question 1?",
      "created_at": "2026-03-18T12:00:00Z"
    },
    // ... 2 more questions
  ]
}
```

### Отправить сообщение

```bash
POST /api/v1/assistant/session/{session_id}/message
Content-Type: application/json

{
  "content": "My answer to the question"
}

Response:
{
  "user_message": { ... },
  "assistant_message": { ... },
  "profile_ready": false
}
```

### Получить историю

```bash
GET /api/v1/assistant/session/{session_id}/messages

Response: [
  { "id": "...", "role": "assistant", "content": "..." },
  { "id": "...", "role": "user", "content": "..." },
  ...
]
```

### Получить профиль

```bash
GET /api/v1/profile/{session_id}

Response:
{
  "id": "uuid",
  "session_id": "uuid",
  "communication_style": "...",
  "attachment_style": "...",
  "partner_preferences": "...",
  "values": "...",
  "created_at": "...",
  "updated_at": "..."
}

# 404 если профиль еще не создан
```

## Структура БД (новые таблицы)

### messages

- `id` (UUID, PK)
- `session_id` (UUID, FK → sessions.id)
- `role` (String: "user" | "assistant")
- `content` (Text)
- `created_at` (DateTime)

### profiles

- `id` (UUID, PK)
- `session_id` (UUID, FK → sessions.id, unique)
- `communication_style` (Text, nullable)
- `attachment_style` (Text, nullable)
- `partner_preferences` (Text, nullable)
- `values` (Text, nullable)
- `raw_data` (JSON, nullable)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Как работает профилирование

1. Пользователь начинает разговор → получает 3 вопроса от AI
2. Отвечает на вопросы → получает follow-up вопросы
3. После 5 ответов → автоматически создается профиль
4. Профиль анализируется OpenAI и сохраняется в БД
5. Frontend показывает "Профиль готов" и отображает панель

## OpenAI Integration

### Production

Использует реальный OpenAI API:
- Модель: `gpt-4o-mini` (настраивается через OPENAI_MODEL)
- 3 вызова для начальных вопросов
- 1 вызов на каждое сообщение пользователя
- 1 вызов для генерации профиля

### Tests

Использует `MockOpenAIService`:
- Возвращает предопределенные ответы
- Не делает реальных API вызовов
- Быстрые и детерминированные тесты

## Архитектура

```
Backend:
  routers/assistant.py → services/assistant.py → models/
                       → services/openai_service.py
                       → services/profile_service.py

Frontend:
  app/assistant/page.tsx → components/ChatMessage
                         → components/ChatInput
                         → components/ProfilePanel
                         → lib/api.ts
```

## Troubleshooting

### OpenAI API ошибки

```bash
# Проверьте ключ
echo $OPENAI_API_KEY

# Проверьте баланс на platform.openai.com
```

### Миграции не применяются

```bash
cd apps/api
source venv/bin/activate
alembic current  # Проверить текущую версию
alembic upgrade head  # Применить все миграции
```

### Тесты падают

```bash
# Backend: убедитесь что используется mock
pytest tests/test_messages.py -v -s

# Frontend: очистите кэш
cd apps/web
rm -rf node_modules/.vite
npm test
```

## Следующие шаги

Step 2 завершен. Готово к Step 3:
- Рекомендации людей (5 в день)
- AI-анализ совместимости
- Swipe интерфейс
