# 🌍 WorldWideNewsTelegramBot

**WorldWideNewsTelegramBot** — це Telegram-бот, який надає користувачам новини з різних країн світу через зручну систему багаторівневого меню. Реалізований із дотриманням принципів модульності, безпечного зберігання даних та масштабованості.

## 🖼️ Скріншоти та gif

![image](https://github.com/user-attachments/assets/435a8bd4-826f-4dc8-95ec-b790591dfc17)
![image](https://github.com/user-attachments/assets/e27ee4e1-1314-4cb4-8332-faaa0f2f894b)
![image](https://github.com/user-attachments/assets/5f7369a4-2160-4097-8dfc-1e04953029bb)
![output](https://github.com/user-attachments/assets/79ebc5b9-6bd6-4d0d-a964-d3e8aac4d056)




## ⚙️ Особливості

- 📋 Багаторівневе навігаційне меню.
- 📌 Збереження стану користувача між сесіями (через `pickle` і Google Cloud Storage).
- 🧱 Клас-базована архітектура (`Action`, `NavigatorController`, `BotController`, `NewsReceiver`).
- 🗞️ Публікація новин у Markdown-форматі.
- 🔐 Інтеграція з Google Cloud Secret Manager для безпечної роботи з токенами та ключами.
- ☁️ **Працює у серверлес-середовищі через Webhook** — без використання long polling.
- 📦 Чітка структура проєкту, легко розширюється та підтримується.


### 🧱 Основні компоненти

- **`main.py`** – Запускає Telegram-бота і починає опитування повідомлень.
- **`bot_controller.py`** – Контролер, який спрямовує вхідні повідомлення до відповідних дій.
- **`bot_model.py` (`NewsReceiver`)** – Основна бізнес-логіка: отримання новин, збереження даних, повернення відповіді.
- **`bot_view.py`** – Відповідає за форматування новин у вигляді Markdown-повідомлень.
- **`navigation_menu.py`** – Реалізація багаторівневого меню для вибору країни або теми.
- **`user_model.py`** – Модель користувача з поточними виборами.
- **`user_storage.py`** – Серіалізація даних користувача та збереження в хмарі.
- **`error_handler.py`** – Централізована обробка помилок.

### ⚙️ Конфігурація та розгортання

- **`requirements.txt`** – Перелік зовнішніх бібліотек (наприклад, `pyTelegramBotAPI`, бібліотеки Google Cloud, `wwntgbotlib`).
- **`cloudbuild.yaml`** – Налаштування для автоматичної збірки й деплою в GCP через Cloud Build.


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

