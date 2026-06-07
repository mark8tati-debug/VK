# Квизы — веб-приложение для live-квизов

MVP платформы для проведения квизов в реальном времени: регистрация участников и организаторов, редактор вопросов, сессии по коду комнаты, WebSocket, лидерборд.

## Ссылки

| Артефакт | URL |
|----------|-----|
| Макеты Figma | https://www.figma.com/design/bowNce537o2YiRGUxFzpAH |
| Пояснительная записка | [docs/POYASNITELNAYA_ZAPISKA.md](docs/POYASNITELNAYA_ZAPISKA.md) |
| Репозиторий | https://github.com/mark8tati-debug/VK |
| Код приложения | [quiz-platform/](quiz-platform/) |

## Быстрый старт

См. [quiz-platform/README.md](quiz-platform/README.md).

```powershell
# Сервер
cd quiz-platform/server
copy .env.example .env
npm install
npm run db:generate
npm run db:push
npm run dev

# Клиент (другой терминал)
cd quiz-platform/client
npm install
npm run dev
```

Приложение: http://localhost:5173

## Структура репозитория

```
MarkovaVK/
├── docs/                 # Пояснительная записка
├── quiz-platform/
│   ├── client/           # React + Vite
│   └── server/           # Node.js + Express + Socket.IO + Prisma
└── scripts/              # Вспомогательные скрипты
```

## Стек

React 18 · Vite · Node.js · Express · Socket.IO · SQLite · Prisma · JWT
