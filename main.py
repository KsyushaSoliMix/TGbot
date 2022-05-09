# Библиотеки
import re
from pathlib import Path
import telebot
import os
import sqlite3
from telebot import types
import googletrans
from googletrans import Translator
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
   (user_id, languages,vocabulary_eng, vocabulary_deu)
VALUES (?, ?, ?, ?);"""

# ----------------------------------------------------------
translator = Translator()

# Функции для получения и сохранения языков:
def get_languages(user_id):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    record = info.fetchone()
    return record[1]


def set_language(user_id, language):
    help_language = get_languages(user_id) + language + "&"
    sqllite_db.cursor.execute('UPDATE users SET languages = ? WHERE user_id = ?', (help_language, user_id))
    sqllite_db.connection.commit()

def write_to_file(data, filename):
    # Преобразование двоичных данных в нужный формат
    with open(filename, 'wb') as file:
        file.write(data)

#сюда закидывается слово из vocab_eng
def after_text_2(message):
   mes=message.text
   info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
   record = info.fetchall()
   for row in record:
       file = row[2]
   vocab_path = Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id))
   write_to_file(file, vocab_path)
   # теперь у нас в файле с компа записаны данные, которые лежат в бд
   #теперь надо добавить новое слово
   result = translator.translate(mes, src="en", dest="ru")
   with open(vocab_path, 'a') as file:
       file.write("\n"+mes+" - "+result.text)
   file_eng = open('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id),
                   "rb").read()
   sqllite_db.cursor.execute('UPDATE users SET vocabulary_eng = ? WHERE user_id = ?',
                             (sqlite3.Binary(file_eng), message.from_user.id))
   sqllite_db.connection.commit()
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

        person_data = (message.from_user.id, "", None,None)
        sqllite_db.cursor.execute(create_users, person_data)
        sqllite_db.connection.commit()

    else:
        bot.send_message(message.chat.id,
                         "Привет " + message.from_user.first_name + "! Готов продолжить обучение?\nВводи команду /study и поехали!!!")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, help_line)

# Выбор языков:
@bot.message_handler(commands=['new_language'])
def new_language_message(message):
    users_languages = get_languages(message.from_user.id)
    split_user_languages = re.split("&", users_languages)
    other_languages = languages

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

    if help_string == "\n":
        bot.send_message(message.chat.id, "Вы еще не выбрали ни одного языка :(")
    else:
        bot.send_message(message.chat.id, help_string)
#делаем словарь для пользователя
@bot.message_handler(commands=['add'])
def creating_quiz(message):
    users_languages = get_languages(message.from_user.id)
    split_user_languages = re.split("&", users_languages)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(split_user_languages)):
        split_user_languages[i] = split_user_languages[i][3:]
    for i in range(0, len(split_user_languages)):
        item = types.KeyboardButton(split_user_languages[i])
        markup.add(item)
    bot.send_message(message.chat.id, "Выберите язык", reply_markup=markup)


@bot.message_handler(commands=['vocab_eng'])
def add_to_eng_vocabulary(message):
    #теперь у нас есть данные из блоба в нашем файле на компе, теперь мы работаем с vocab_path файлом, в него
    #будем записывать данные пользователя
    keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
    msg = bot.send_message(message.from_user.id, "Запиши слово, которое хочешь добавить в словарь в таком формате: *слово*", reply_markup = keyboard1)
    bot.register_next_step_handler(msg, after_text_2)



@bot.message_handler(commands=['get_eng_vocab'])
def new_language_message(message):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchall()
    for row in record:
        file = row[2]
    vocab_path = Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id))
    write_to_file(file, vocab_path)
    f = open(vocab_path, "rb")
    bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['quiz'])
def new_language_message(message):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchall()
    for row in record:
        file = row[2]
    vocab_path = Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id))
    write_to_file(file, vocab_path)
    dictionary = {}

    with open(vocab_path,"r") as file1:
        file1.readline()
        while True:
            # считываем строку
            line = file1.readline()
            # прерываем цикл, если строка пустая
            if not line:
                break

            words = line.split(" - ")
            orig_word = words[0]
            translated_word = words[1]
            dictionary[orig_word] = translated_word
    print(dictionary)

@bot.message_handler(content_types=['text'])
def languages_handling(message):
    a = telebot.types.ReplyKeyboardRemove()
    if message.text == "🇬🇧 English":
        str = "🇬🇧 English"
        bot.send_message(message.chat.id, 'Now you are a englishman', reply_markup=a)
        set_language(message.from_user.id, str)
        # file = Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)).touch()
        # done_file = convert_to_binary_data('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id))
        # sqllite_db.cursor.execute('UPDATE users SET vocabulary_eng = ? WHERE user_id = ?', (sqlite3.Binary(file_eng), user_id))
        # sqllite_db.connection.commit()
        Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)).touch()
        open('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id), "w").write(
            "English vocabulary")
        file_eng = open('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id),
                        "rb").read()
        sqllite_db.cursor.execute('UPDATE users SET vocabulary_eng = ? WHERE user_id = ?',
                                  (sqlite3.Binary(file_eng), message.from_user.id))
        sqllite_db.connection.commit()


    elif message.text == "🇩🇪 Deutsch":
        str = "🇩🇪 Deutsch"
        bot.send_message(message.chat.id, 'Jetzt du bist Deutsch Person', reply_markup=a)
        set_language(message.from_user.id, str)
        Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_deu.txt'.format(message.chat.id)).touch()
        open('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_deu.txt'.format(message.chat.id), "w").write(
            "Deutch vocabulary")
        file_eng = open('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_deu.txt'.format(message.chat.id),
                        "rb").read()
        sqllite_db.cursor.execute('UPDATE users SET vocabulary_deu = ? WHERE user_id = ?',
                                  (sqlite3.Binary(file_eng), message.from_user.id))
        sqllite_db.connection.commit()
    elif message.text == "🇷🇺 Русский":
        bot.send_message(message.chat.id, 'Уйди отсюда, пидор грязный')

# ----------------------------------------------------------
bot.polling(none_stop=True)
