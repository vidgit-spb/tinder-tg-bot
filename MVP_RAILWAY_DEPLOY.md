# MVP Deploy on Railway (Single Service)

This repo now runs **bot + Mini App** in one process:

- Telegram bot polling runs in a background thread
- Mini App API + frontend runs in FastAPI

---

## 1) Railway service

- Source: this GitHub repo
- Start command:

```bash
uvicorn miniapp_server:app --host 0.0.0.0 --port $PORT
```

The same command is already in `Procfile`.

- Required variables:

```bash
BOT_TOKEN=...
BOT_USERNAME=your_bot_username_without_at
MINI_APP_URL=https://<your-service>.up.railway.app
MESSAGE_ENCRYPTION_KEY=<long-random-secret>
SESSION_SECRET=<another-long-random-secret>
RUN_BOT_IN_PROCESS=1
DATABASE_PATH=dating_bot.db
```

After first deploy, copy the public URL and set it to `MINI_APP_URL`, then redeploy once.

---

## 2) Telegram test flow

1. Open bot and run `/start`
2. Complete profile in bot or Mini App
3. Tap **📱 Open Mini App**
4. Test swipe left/right in Mini App
5. Create match from second account
6. Test internal chat (messages only in app, no direct Telegram contacts)
7. Test gifts
8. Test share button

---

## 3) Security included in MVP

- Telegram Mini App user verification via `initData` HMAC validation
- Short-lived app session token signed on server
- Messages encrypted at rest in DB when `MESSAGE_ENCRYPTION_KEY` is set
- Chat/gifts only allowed for matched users
