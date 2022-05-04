# Библиотеки
import re

import telebot
from telebot import types

import sqllite_db

# Токен и создание бота

token = '5305392177:AAGRLxjBJ43TgZSo7qC8XoXRJ75bKCzh7Fk'
bot = telebot.TeleBot(token)
# ----------------------------------------------------------

# Переменные для команд

languages = ["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇺 Русский"]

help_line = "/new_language - добавляет новый язык.\n" \
            "/my_languages - показывает уже изучаемые вами языки\n" \
            "/study *язык* - команда для продолжения изучения языка.\n"

create_users = """
INSERT INTO users 
   (user_id, languages)
VALUES (?, ?);"""



# ----------------------------------------------------------


@bot.message_handler(commands=['start'])
def start_message(message):
    # Создаем нового юзера и добавляем его в базу данных, с проверкой на то, был ли он до этого зарегестрирован
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    info.fetchone()
    if info.fetchone() is None:
        bot.send_message(message.chat.id, "Привет " + message.from_user.first_name + "!\n" \
                                                                                     "Study language bot поможет тебе в изучении разных иностранных языков.\n" \
                                                                                     "Введи /help для того, чтобы посмотреть функционал.")
        person_data = (message.from_user.id, "")
        sqllite_db.cursor.execute(create_users, person_data)
        sqllite_db.connection.commit()
    else:
        bot.send_message(message.chat.id,
                         "Привет " + message.from_user.first_name + "! Готов продолжить обучение?\nВводи команду /study и поехали!!!")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, help_line)


# Функции для получения и сохранения языков:
def get_languages(user_id):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    record = info.fetchone()
    return record[1]


def set_language(user_id, language):
    help_language = get_languages(user_id) + language + "&"
    sqllite_db.cursor.execute('UPDATE users SET languages = ? WHERE user_id = ?', (help_language, user_id))
    sqllite_db.connection.commit()
    print(get_languages(user_id))


# Выбор языков:
@bot.message_handler(commands=['new_language'])
def new_language_message(message):
    users_languages = get_languages(message.from_user.id)
    split_user_languages = re.split("&", users_languages)
    other_languages = languages
    print(split_user_languages)
    for i in range(0, len(split_user_languages)):
        if other_languages.__contains__(split_user_languages[i]):
            other_languages.remove(split_user_languages[i])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(other_languages)):
        item = types.KeyboardButton(other_languages[i])
        markup.add(item)
    bot.send_message(message.chat.id, "Выберите язык", reply_markup=markup)


@bot.message_handler(commands=['my_languages'])
def get_my_languages_message(message):
    users_languages = get_languages(message.from_user.id)
    split_user_languages = re.split("&", users_languages)
    help_string = ""
    for i in range(0, len(split_user_languages)):
        help_string += split_user_languages[i] + "\n"
    print(help_string)
    if help_string == "\n":
        bot.send_message(message.chat.id, "Вы еще не выбрали ни одного языка :(")
    else:
        bot.send_message(message.chat.id, help_string)


@bot.message_handler(content_types=['text'])
def languages_handling(message):
    a = telebot.types.ReplyKeyboardRemove()
    if message.text == "🇬🇧 English":
        str = "🇬🇧 English"
        bot.send_message(message.chat.id, 'Now you are a englishman', reply_markup=a)
        set_language(message.from_user.id, str)
    elif message.text == "🇩🇪 Deutsch":
        str = "🇩🇪 Deutsch"
        bot.send_message(message.chat.id, 'Jetzt du bist Deutsch Person', reply_markup=a)
        set_language(message.from_user.id, str)
    elif message.text == "🇷🇺 Русский":
        bot.send_message(message.chat.id, 'Уйди отсюда, пидор грязный')


# ----------------------------------------------------------
bot.polling(none_stop=True)
