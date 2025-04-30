# 📰 WorldWideNews Telegram Bot

Це Telegram-бот, який дозволяє користувачам переглядати новини з усього світу через багаторівневе меню навігації. Він використовує:
- `pyTelegramBotAPI` для Telegram-взаємодії
- Google Cloud Storage та Secret Manager для зберігання даних
- Власну бібліотеку `wwntgbotlib` для архітектури бота

## ⚙️ Функціональність

- Вибір новин за країнами
- Багаторівневе меню
- Збереження стану навігації кожного користувача
- Форматування новин за допомогою Markdown
- Серіалізація стану через `pickle`
- Архітектура на основі патерну "дія як клас"

Використані технології
- Python 3.10+
- pyTelegramBotAPI
- Google Cloud Storage
- Google Secret Manager

Посилання на бот: https://t.me/EarthNewsEpicBot
