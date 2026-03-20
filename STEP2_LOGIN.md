# Yellow - Вход и восстановление истории

## ✅ Что добавлено

**Новый функционал:**
- 🔐 Форма входа по User ID
- 💾 Автоматическое сохранение user_id в localStorage
- 📜 Восстановление всей истории чата при повторном входе
- 👤 Отображение user_id в хедере
- 🚪 Кнопка "Выйти"
- 🔄 Автоматический вход при перезагрузке страницы

**Backend:**
- ✅ GET `/api/v1/assistant/user/{user_id}/session` - получить последнюю сессию пользователя
- ✅ Если сессии нет - создаёт новую
- ✅ Если есть - возвращает существующую
- ✅ 3 новых теста

**Frontend:**
- ✅ Форма входа с полем User ID
- ✅ Автоматическое восстановление истории
- ✅ Автоматическая загрузка профиля (если готов)
- ✅ localStorage для сохранения user_id
- ✅ Кнопка выхода
- ✅ 2 новых теста

## 🎯 Как это работает

### Первый вход (новый пользователь)

1. Пользователь вводит user_id (например: "ivan")
2. Backend создаёт новую сессию
3. Автоматически вызывается `/start` → 3 вопроса от AI
4. user_id сохраняется в localStorage
5. Начинается новый разговор

### Повторный вход (существующий пользователь)

1. Пользователь вводит user_id (например: "artem")
2. Backend находит последнюю сессию этого пользователя
3. Frontend загружает всю историю сообщений
4. Если профиль готов - загружает и отображает его
5. Пользователь может продолжить разговор

### Автоматический вход

1. При открытии страницы проверяется localStorage
2. Если найден сохранённый user_id - автоматический вход
3. История восстанавливается
4. Пользователь сразу видит свой чат

## 📝 Примеры использования

### API

```bash
# Получить сессию для пользователя (создаст новую или вернёт существующую)
curl http://localhost:8000/api/v1/assistant/user/artem/session

# Ответ для нового пользователя:
{
  "session_id": "uuid",
  "status": "created"
}

# Ответ для существующего пользователя:
{
  "session_id": "uuid",
  "status": "existing"
}
```

### Frontend Flow

```typescript
// 1. Пользователь вводит user_id
const response = await apiClient.getUserSession('artem')

// 2. Если status === 'existing' - загружаем историю
if (response.status === 'existing') {
  const messages = await apiClient.getMessages(response.session_id)
  const profile = await apiClient.getProfile(response.session_id)
}

// 3. Если status === 'created' - начинаем новый разговор
if (response.status === 'created') {
  const conversation = await apiClient.startConversation(response.session_id)
}
```

## 🧪 Тестирование

### Backend тесты

```bash
cd apps/api
source venv/bin/activate
pytest tests/test_user_session.py -v

# Результат: 3/3 passed
# - test_get_user_session_creates_new
# - test_get_user_session_returns_existing
# - test_get_user_session_returns_latest
```

### Frontend тесты

```bash
cd apps/web
npm test tests/pages/assistant.test.tsx

# Результат: 7/7 passed
# - renders login form initially
# - renders initial questions after login
# - shows profile status badge after login
# - sends message and displays response
# - updates profile status when profile is ready
# - displays profile panel when profile is ready
# - restores chat history for existing user ← НОВЫЙ
```

### Ручное тестирование

1. Откройте http://localhost:3000/assistant
2. Войдите как **"artem"**:
   - ✅ Увидите 13 сообщений из истории
   - ✅ Справа панель с готовым профилем
   - ✅ Можете продолжить разговор

3. Нажмите **"Выйти"**

4. Войдите как **"maria"** (новый пользователь):
   - ✅ Увидите 3 начальных вопроса
   - ✅ История пустая
   - ✅ Начните отвечать на вопросы

5. Обновите страницу (F5):
   - ✅ Автоматически войдёте как "maria"
   - ✅ История сохранится

6. Выйдите и войдите снова как **"artem"**:
   - ✅ Вся история восстановится!

## 🔧 Технические детали

### localStorage

```javascript
// Сохранение
localStorage.setItem('yellow_user_id', userId)

// Загрузка при старте
const savedUserId = localStorage.getItem('yellow_user_id')

// Очистка при выходе
localStorage.removeItem('yellow_user_id')
```

### Backend логика

```python
def get_user_latest_session(self, user_id: str) -> Optional[Session]:
    """Get the latest session for a user."""
    return self.db.query(Session).filter_by(
        user_id=user_id
    ).order_by(Session.created_at.desc()).first()
```

### Frontend логика

```typescript
// При входе
const sessionResponse = await apiClient.getUserSession(userId)

if (sessionResponse.status === 'existing') {
  // Загрузить историю
  const messages = await apiClient.getMessages(sessionResponse.session_id)
  setMessages(messages)
  
  // Попытаться загрузить профиль
  try {
    const profile = await apiClient.getProfile(sessionResponse.session_id)
    setProfile(profile)
    setProfileStatus('ready')
  } catch {
    // Профиль ещё не готов
  }
} else {
  // Начать новый разговор
  const conversation = await apiClient.startConversation(sessionResponse.session_id)
  setMessages(conversation.messages)
}
```

## 📊 Итоговая статистика

**Backend:**
- 22 теста ✅
- 4 endpoints для сессий
- 3 endpoints для сообщений
- 1 endpoint для профиля
- 1 endpoint для входа пользователя

**Frontend:**
- 22 теста ✅
- Форма входа
- Восстановление истории
- Автоматический вход
- Выход

**Total: 44/44 тестов проходят** ✅

## 🚀 Готово к использованию!

Теперь Yellow имеет полноценную систему входа:
- ✅ Каждый пользователь имеет свою историю
- ✅ История сохраняется между сессиями
- ✅ Профиль привязан к пользователю
- ✅ Можно выйти и войти под другим user_id
- ✅ Автоматический вход при возврате на страницу
