# SSAU Schedule

Монорепозиторий бота расписания СНИУ.

```
.
├── backend/    # Telegram-бот + воркер + REST API (Python, clean architecture)
└── frontend/   # Веб: страница авторизации в СНИУ (React + TypeScript + Vite)
```

У каждой части — свой `README.md` и свой набор правил/доков.

## Backend
Python, чистая архитектура: бот (aiogram), воркер (уведомления), REST API (FastAPI),
SQLite + alembic, Valkey-кэш. Запуск, гейт и конвенции — в [backend/README.md](backend/README.md).
Правила и архитектура — в [backend/docs/](backend/docs/) (`AGENT_MISTAKES.md`, `WORK_CONTEXT.md`,
`PROMPT_TEMPLATE.md`).

```bash
cd backend
make run-bot        # бот
make run-worker     # воркер
make run-api        # REST API
make check          # гейт: ruff + mypy + pytest
```

## Frontend
React 19 + TypeScript + Vite + Tailwind v4 + shadcn-style UI. Страница авторизации в стилистике
СНИУ. Запуск и паттерны — в [frontend/README.md](frontend/README.md) и
[frontend/docs/FRONTEND_PATTERNS.md](frontend/docs/FRONTEND_PATTERNS.md).

```bash
cd frontend
npm install
npm run dev         # http://localhost:5173/auth?token=<state>
```

## Как это связано
Бот шлёт пользователю ссылку на `frontend` (`/auth?token=…`); страница собирает логин/пароль СНИУ и
вызывает `backend` (`POST /internal/v1/auth/ssau`), который логинится в ЛК и подключает расписание.
Так креды вводятся на защищённой странице, а не в чате Telegram.
