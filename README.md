# 🌍 WorldWideNewsTelegramBot

**WorldWideNewsTelegramBot** — це Telegram-бот, який надає користувачам новини з різних країн світу через зручну систему багаторівневого меню. Реалізований із дотриманням принципів модульності, безпечного зберігання даних та масштабованості.

## 🖼️ Скріншоти та відео

![image](https://github.com/user-attachments/assets/435a8bd4-826f-4dc8-95ec-b790591dfc17)
![image](https://github.com/user-attachments/assets/e27ee4e1-1314-4cb4-8332-faaa0f2f894b)
![image](https://github.com/user-attachments/assets/5f7369a4-2160-4097-8dfc-1e04953029bb)
<video src="[URL_ДО_ВІДЕО.mp4](https://github.com/user-attachments/assets/b4d9682d-dcb4-4b75-a76b-9923d858edd8)" controls width="100%"></video>



## ⚙️ Особливості

- 📋 Багаторівневе навігаційне меню.
- 📌 Збереження стану користувача між сесіями (через `pickle` і Google Cloud Storage).
- 🧱 Клас-базована архітектура (`Action`, `NavigatorController`, `BotController`, `NewsReceiver`).
- 🗞️ Публікація новин у Markdown-форматі.
- 🔐 Інтеграція з Google Cloud Secret Manager для безпечної роботи з токенами та ключами.
- ☁️ **Працює у серверлес-середовищі через Webhook** — без використання long polling.
- 📦 Чітка структура проєкту, легко розширюється та підтримується.

## 🗂️ Основні модулі

- `main.py` — стартова точка застосунку (обробка webhook-запитів).
- `wwntgbotlib/` — модульна бібліотека логіки бота:
  - `core/` — основні класи керування ботом і навігацією.
  - `actions/` — дії, які виконує бот у відповідь на вибір користувача.
  - `helpers/` — утиліти для форматування, логування та роботи з часом.
- `gcp/` — взаємодія з Google Cloud Storage та Secret Manager.
- `tests/` — модульні тести для перевірки окремих компонентів.
- `config/` — конфігураційні файли (уникати додавання чутливих даних!).

## 🛠️ Технологічний стек

- Python 3.10+
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Google Cloud Platform:
  - Cloud Storage
  - Secret Manager
- Pickle (для серіалізації станів навігатора)

## 🚀 Розгортання (загальні кроки)

1. Створіть Telegram-бота через [BotFather](https://t.me/BotFather).
2. Налаштуйте Google Cloud:
   - Створіть bucket у Cloud Storage.
   - Збережіть секрети в Secret Manager (`BOT_TOKEN`, `PROJECT_ID`, тощо).
3. Задеплойте функцію на Google Cloud Functions або інший серверлес-сервіс із підтримкою webhook.

> ❗ Цей бот не використовує long polling — запуск відбувається за подіями через Webhook.

### 🔗 Запустити бота  
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)]([https://t.me/WorldWideNewsChannelBot](https://t.me/EarthNewsEpicBot))


## 📎 Ліцензія

Цей проєкт поширюється під ліцензією MIT.

---

