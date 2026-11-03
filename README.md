# Telegram-бот для приёма заявок

Бот для малого бизнеса: меню (услуги, цены, контакты) и форма заявки,
которая приходит владельцу в личные сообщения.

Стек: Python, aiogram 3 (FSM), python-dotenv.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # впишите BOT_TOKEN и ADMIN_ID
python bot.py
```

- `BOT_TOKEN` — токен от @BotFather.
- `ADMIN_ID` — ваш числовой Telegram ID (узнать у @userinfobot).
- `BUSINESS_NAME` — название, которое увидит клиент.

## Как адаптировать под клиента
Тексты услуг, цен и контактов лежат в константах `SERVICES`, `PRICES`, `CONTACTS` в `bot.py`.
