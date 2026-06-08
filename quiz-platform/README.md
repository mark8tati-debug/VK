# Квизы — MVP платформы live-квизов

Веб-приложение для организаторов и участников: создание квизов, live-сессии по коду комнаты, ответы в реальном времени, лидерборд.

## Ссылки

- **Макеты Figma:** https://www.figma.com/design/bowNce537o2YiRGUxFzpAH/%D0%9A%D0%B2%D0%B8%D0%B7%D1%8B?node-id=19-2&t=7KKZVgCaFoJHt23K-1
- **Пояснительная записка:** [docs/POYASNITELNAYA_ZAPISKA.md](../docs/POYASNITELNAYA_ZAPISKA.md)

## Стек

| Слой | Технология |
|------|------------|
| Клиент | React 18, Vite, React Router |
| Сервер | Node.js, Express |
| Real-time | Socket.IO |
| БД | SQLite + Prisma ORM |
| Auth | JWT + bcrypt |

## Быстрый старт

### 1. Сервер

```bash
cd server
cp .env.example .env
npm install
npm run db:generate
npm run db:push
npm run dev
```

API и WebSocket: http://localhost:3001

### 2. Клиент

```bash
cd client
npm install
npm run dev
```

Приложение: http://localhost:5173

## Сценарий проверки MVP

1. Зарегистрируйте **организатора** → «Мои квизы» → создайте квиз, добавьте вопросы.
2. Нажмите **Запустить** → скопируйте код комнаты (KVIZ-…).
3. В другом браузере зарегистрируйте **участника** → «Войти в квиз» → введите код.
4. Организатор: **Старт сессии** → **Следующий вопрос**.
5. Участник отвечает, пока вопрос активен.
6. **Завершить квиз** → лидерборд на странице итогов и в профиле.

## API (кратко)

- `POST /api/auth/register` · `POST /api/auth/login`
- `GET/POST /api/quizzes` · `POST /api/quizzes/:id/questions`
- `POST /api/sessions` · `POST /api/sessions/join` · `GET /api/sessions/:id/leaderboard`

## Socket.IO события

| Событие | Направление | Описание |
|---------|-------------|----------|
| `join_session` | client → server | Подключение к комнате |
| `start_session` | organizer | Старт квиза |
| `show_question` | organizer | Показ вопроса всем |
| `submit_answer` | participant | Ответ (только при активном вопросе) |
| `end_question` | organizer | Закрыть приём ответов |
| `end_session` | organizer | Финиш + лидерборд |
