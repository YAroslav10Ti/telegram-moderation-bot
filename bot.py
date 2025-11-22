import telebot
from telebot import types
import sqlite3
import time

# ЗАМЕНИТЕ НА ВАШ ТОКЕН!
bot = telebot.TeleBot('8528721355:AAGF3rTe5mIxl35NsDyJbtye-LRdWAtttsk')

# Список запрещенных слов
BAD_WORDS = ['мат', 'спам', 'реклама']

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('moderation.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS warns (
        user_id INTEGER,
        chat_id INTEGER,
        warnings INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, chat_id)
    )''')
    conn.commit()
    conn.close()

init_db()

# Команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "🤖 Я бот-модератор! Добавьте меня в группу.")
    else:
        bot.send_message(message.chat.id, "✅ Бот-модератор активирован! /help")

# Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🛠 Команды:
/help - справка
/warns - мои предупреждения
/rules - правила чата

Автоматически:
• Приветствует новых участников
• Удаляет сообщения с матом
• Выдает предупреждения
    """
    bot.send_message(message.chat.id, help_text)

# Команда /rules
@bot.message_handler(commands=['rules'])
def rules_command(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "❌ Правила есть только в группах!")
        return
    
    rules_text = "📜 Правила:\n1. Не материться\n2. Не спамить\n3. Уважать друг друга"
    bot.send_message(message.chat.id, rules_text)

# Приветствие новых участников
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_members(message):
    for member in message.new_chat_members:
        welcome_text = f"👋 Добро пожаловать, {member.first_name}!\nПрочитай правила: /rules"
        bot.send_message(message.chat.id, welcome_text)

# Фильтр запрещенных слов
@bot.message_handler(content_types=['text'])
def check_bad_words(message):
    # Работаем только в группах
    if message.chat.type == 'private':
        return
    
    # Пропускаем команды
    if message.text.startswith('/'):
        return
    
    message_text = message.text.lower()
    
    # Проверяем на запрещенные слова
    for word in BAD_WORDS:
        if word in message_text:
            try:
                # Удаляем сообщение
                bot.delete_message(message.chat.id, message.message_id)
                
                # Добавляем предупреждение
                add_warning(message.from_user.id, message.chat.id)
                warns = get_warnings(message.from_user.id, message.chat.id)
                
                # Отправляем предупреждение
                warning_msg = f"⚠️ {message.from_user.first_name}, не используйте запрещенные слова! Предупреждение {warns}/3"
                bot.send_message(message.chat.id, warning_msg)
                
                # Если 3 предупреждения - бан
                if warns >= 3:
                    try:
                        bot.ban_chat_member(message.chat.id, message.from_user.id)
                        bot.send_message(message.chat.id, f"🚫 {message.from_user.first_name} забанен!")
                    except Exception as e:
                        print(f"Ошибка бана: {e}")
                
            except Exception as e:
                print(f"Ошибка: {e}")
            break

# Вспомогательные функции для БД
def add_warning(user_id, chat_id):
    conn = sqlite3.connect('moderation.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute('SELECT warnings FROM warns WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    result = cur.fetchone()
    
    if result:
        new_warns = result[0] + 1
        cur.execute('UPDATE warns SET warnings = ? WHERE user_id = ? AND chat_id = ?', 
                   (new_warns, user_id, chat_id))
    else:
        cur.execute('INSERT INTO warns (user_id, chat_id, warnings) VALUES (?, ?, 1)', 
                   (user_id, chat_id))
    
    conn.commit()
    conn.close()
    return new_warns if result else 1

def get_warnings(user_id, chat_id):
    conn = sqlite3.connect('moderation.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute('SELECT warnings FROM warns WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот-модератор запущен!")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(15)