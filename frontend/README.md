# SSAU Schedule — Frontend

Веб-часть бота расписания СНИУ. Главная задача — **страница авторизации в СНИУ**: пользователь
вводит логин/пароль на защищённой странице (а не в чате Telegram), бэкенд логинится в ЛК и
подключает расписание.

## Стек
- **Vite + React 19 + TypeScript** (strict)
- **Tailwind CSS v4** (CSS-first, токены в `@theme`) + **shadcn-style UI** (`src/components/ui`)
- **TanStack Query** — серверный стейт · **React Hook Form + Zod** — формы/валидация
- **React Router** · **Vitest + Testing Library** — тесты · ESLint + Prettier

## Запуск
```bash
npm install
cp .env.example .env      # задай VITE_API_BASE_URL (адрес backend API)
npm run dev               # http://localhost:5173/auth?token=<state>
```

## Гейт (прогонять перед коммитом)
```bash
npm run lint
npm run typecheck
npm test
npm run build
```

## Структура
```
src/
  components/ui/      # дизайн-система (Button, Input, Card, Alert, …) — shadcn-style
  features/
    auth/            # фича авторизации: страница, форма, схема, api, хук, тест
  lib/               # кросс-каттинг: api-client, query-client, utils(cn)
  index.css          # Tailwind + токены бренда СНИУ (@theme)
  main.tsx, App.tsx  # вход + роутинг
```

Правила и конвенции — [docs/FRONTEND_PATTERNS.md](docs/FRONTEND_PATTERNS.md).

## Контракт с backend
Страница ждёт endpoint `POST {VITE_API_BASE_URL}/internal/v1/auth/ssau`:
```jsonc
// запрос
{ "token": "<подписанный state из ссылки бота>", "login": "...", "password": "..." }
// ответ
{ "status": "success" | "profile_fetch_error" | "profile_not_found", "group_name": "6132-..." | null }
```
`token` привязывает форму к Telegram-аккаунту (бот генерит ссылку `/auth?token=…`).
