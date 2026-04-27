# Telegram Moderation Bot

Бот для модерации Telegram-групп с автоматическим контролем сообщений.

## Функциональность

- Приветствие новых участников
- Фильтрация запрещённых слов
- Автоматическое удаление сообщений
- Система предупреждений (warns)
- Бан пользователя после 3 нарушений
- Команды:
/help — справка  
/rules — правила  
/warns — количество предупреждений  

## Технологии

- Python
- pyTelegramBotAPI
- SQLite
- dotenv

## Структура

- bot.py — основной файл бота
- requirements.txt — зависимости
- moderation.db — база данных (создаётся автоматически)

## Установка

```bash
python3 -m venv bot_env
source bot_env/bin/activate
pip install -r requirements.txt