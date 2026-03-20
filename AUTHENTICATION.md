# Аутентификация с паролем и JWT

## Обзор

Реализована полная система аутентификации с регистрацией, входом и JWT токенами.

## Технологии

- **Хеширование паролей**: bcrypt через `passlib[bcrypt]`
- **JWT токены**: `python-jose[cryptography]`
- **Валидация email**: `email-validator`
- **Срок действия токена**: 7 дней (настраивается через `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)

## Backend API

### Новые эндпоинты

#### POST /api/v1/auth/register
Регистрация нового пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Ошибки:**
- `400`: Email или username уже заняты
- `422`: Невалидные данные (короткий пароль, невалидный email)

#### POST /api/v1/auth/login
Вход существующего пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Ошибки:**
- `401`: Неверный email или пароль

#### GET /api/v1/auth/me
Получение информации о текущем пользователе.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "created_at": "2026-03-18T17:47:51.652816"
}
```

**Ошибки:**
- `401`: Невалидный или истёкший токен

### Защищённые эндпоинты

Все эндпоинты `/api/v1/assistant/*` и `/api/v1/profile/*` теперь требуют JWT токен в заголовке `Authorization: Bearer <token>`.

## Модель данных

### Таблица users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

### Связь с sessions

```sql
ALTER TABLE sessions
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
```

## Frontend

### Компоненты

#### AuthForm
Универсальная форма для входа и регистрации с переключением режимов.

**Props:**
```typescript
{
  mode: 'login' | 'register'
  onSubmit: (data: UserLoginRequest | UserRegisterRequest) => Promise<void>
  onToggleMode: () => void
  error?: string
  loading?: boolean
}
```

### Хранение токена

JWT токен сохраняется в `localStorage` с ключом `yellow_token`.

### Auto-login

При загрузке страницы `/assistant`:
1. Проверяется наличие токена в `localStorage`
2. Если токен есть, делается запрос `GET /auth/me`
3. При успехе пользователь автоматически входит
4. При ошибке токен удаляется и показывается форма входа

## Миграции

### 004_create_users_table.py
- Создаёт таблицу `users`
- Добавляет временную колонку `user_id_new` в `sessions`

### 005_migrate_sessions_to_users.py
- Мигрирует существующие сессии:
  - Для каждого уникального `user_id` (строка) создаётся запись в `users`
  - Email: `{old_user_id}@yellow.local`
  - Username: `{old_user_id}`
  - Password: dummy хеш
- Обновляет `sessions.user_id_new` на UUID из `users`
- Удаляет старую колонку `sessions.user_id`
- Переименовывает `user_id_new` → `user_id`
- Добавляет foreign key constraint

## Тестирование

### Backend тесты

```bash
cd apps/api
pytest tests/test_auth.py -v
```

**Покрытие:**
- ✅ Регистрация нового пользователя
- ✅ Регистрация с дублирующимся email
- ✅ Регистрация с дублирующимся username
- ✅ Регистрация с невалидным email
- ✅ Регистрация с коротким паролем
- ✅ Вход с правильными данными
- ✅ Вход с неверным паролем
- ✅ Вход с несуществующим email
- ✅ Получение текущего пользователя
- ✅ Получение с невалидным токеном
- ✅ Доступ к защищённым эндпоинтам без токена
- ✅ Доступ к защищённым эндпоинтам с токеном

### Frontend тесты

```bash
cd apps/web
npm test
```

**Покрытие:**
- ✅ Рендеринг формы входа
- ✅ Рендеринг формы регистрации
- ✅ Переключение между режимами
- ✅ Отправка данных регистрации
- ✅ Отправка данных входа
- ✅ Валидация формы

### Ручное тестирование

```bash
# 1. Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "testpass123"}'

# 2. Вход
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# 3. Получение профиля
TOKEN="<token_from_login>"
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Создание сессии
curl -X POST http://localhost:8000/api/v1/assistant/session \
  -H "Authorization: Bearer $TOKEN"
```

## Конфигурация

### Backend (.env)

```env
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 дней
```

### Frontend (.env)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Безопасность

### Пароли
- Минимальная длина: 8 символов
- Хеширование: bcrypt с автоматической солью
- Пароли обрезаются до 72 байт (ограничение bcrypt)

### JWT
- Алгоритм: HS256
- Payload: `{"sub": "<user_id>", "exp": <timestamp>}`
- Срок действия: 7 дней (настраивается)

### Email
- Валидация через `email-validator`
- Проверка на существующие email при регистрации
- Уникальность в БД

### Username
- Минимальная длина: 3 символа
- Максимальная длина: 50 символов
- Уникальность в БД

## Статистика

- **Backend файлов**: 4 новых, 7 изменённых
- **Frontend файлов**: 2 новых, 3 изменённых
- **Миграций**: 2 новых
- **Тестов**: 12 новых backend, 6 новых frontend
- **Все тесты**: ✅ 31/31 backend, ✅ 26/26 frontend
