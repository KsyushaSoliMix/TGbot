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
import random
import multiprocessing
import schedule
import datetime
import time

# Токен и создание бота

token = '5305392177:AAGRLxjBJ43TgZSo7qC8XoXRJ75bKCzh7Fk'
bot = telebot.TeleBot(token)

# ----------------------------------------------------------

# Переменные для команд

translator = Translator()

languages = ["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇺 Русский"]

create_users = """
INSERT INTO users 
   (user_id, languages,vocabulary_eng, vocabulary_deu, days)
VALUES (?, ?, ?, ?, ?);"""

# ----------------------------------------------------------

correct_word_in_russian_from_eng = ''
correct_word_in_russian_from_deu = ''


# Функции для получения и сохранения языков:
def get_languages(user_id):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    record = info.fetchone()
    return record[1]


def set_language(user_id, language):
    help_language = get_languages(user_id) + language + "&"
    sqllite_db.cursor.execute('UPDATE users SET languages = ? WHERE user_id = ?', (help_language, user_id))
    sqllite_db.connection.commit()


# Функции для получения дней недели
def get_days(user_id):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    record = info.fetchone()
    return record[4]


def set_day(user_id, day):
    help_day = get_days(user_id) + day + "&"
    sqllite_db.cursor.execute('UPDATE users SET days = ? WHERE user_id = ?', (help_day, user_id))
    sqllite_db.connection.commit()


# Функции для отправления сообщений по времени
def nine(id):
    bot.send_message(id, "Новый день - новая жизнь! Пора продолжать изучать твой любимый иностранный язык!"
                         " Не забудь, что вечером мы будем ждать твой отчет об проделанной работе.\nВводи команду /study, чтобы продолжить обучение. ")


def four(id):
    bot.send_message(id, "Прошло уже пол дня! А ты уже сел за изучения иностранных? Если нет - то самое время."
                         " Не забудь, что вечером мы будем ждать твой отчет об проделанной работе.\nВводи команду /study, чтобы продолжить обучение. ")


def ten(id):
    bot.send_message(id,
                     "Нужно больше ОТЧЕТОВ!!! День прошел, он же был продуктивный, да..? Это мы сейчас и узнаем!\n Присылай свой отчет следующим сообщением и иди отдыхай.\n"
                     "Если отдыхать не хочется, то жми /study и погнали дальше!")


# сюда закидывается слово из vocab_eng
def after_text_2(message):
    mes = message.text
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchone()
    if record[2] != None:
        vocabulary = record[2]
    else:
        vocabulary = ""
    help_string = str(vocabulary) + str(mes) + ","
    sqllite_db.cursor.execute('UPDATE users SET vocabulary_eng = ? WHERE user_id = ?',
                              (help_string, message.from_user.id))
    sqllite_db.connection.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # здесь нужен инлайн
    item1 = types.KeyboardButton("Да eng")
    markup.add(item1)
    item1 = types.KeyboardButton("Выйти в главное меню")
    markup.add(item1)
    bot.send_message(message.chat.id, "Продолжить добавлять слова?", reply_markup=markup)


def after_text_1(message):
    mes = message.text
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchone()
    if record[3] != None:
        vocabulary = record[2]
    else:
        vocabulary = ""
    help_string = str(vocabulary) + str(mes) + ","
    sqllite_db.cursor.execute('UPDATE users SET vocabulary_deu = ? WHERE user_id = ?',
                              (help_string, message.from_user.id))
    sqllite_db.connection.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # здесь нужен инлайн
    item1 = types.KeyboardButton("Да deu")
    markup.add(item1)
    item1 = types.KeyboardButton("Выйти в главное меню")
    markup.add(item1)
    bot.send_message(message.chat.id, "Продолжить добавлять слова?", reply_markup=markup)


# ----------------------------------------------------------


@bot.message_handler(commands=['start'])
def start_message(message):
    # Создаем нового юзера и добавляем его в базу данных, с проверкой на то, был ли он до этого зарегестрирован
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchone()
    if record is None:
        bot.send_message(message.chat.id, "Привет, " + message.from_user.first_name + "!\n" \
                                                                                      "Study language bot поможет тебе в изучении разных иностранных языков.\n" \
                                                                                      "Введи /help для того, чтобы посмотреть функционал.")

        person_data = (message.from_user.id, "", None, None, "")
        sqllite_db.cursor.execute(create_users, person_data)
        sqllite_db.connection.commit()

    else:
        bot.send_message(message.chat.id,
                         "Привет, " + message.from_user.first_name + "! Готов продолжить обучение?\nВводи команду /study и поехали!!!")


@bot.message_handler(commands=['study'])
def study(message):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchone()
    if record[0] != None:
        users_languages = get_languages(message.from_user.id)
        split_user_languages = re.split("&", users_languages)

        help_string = ""
        for i in range(0, len(split_user_languages)):
            help_string += split_user_languages[i] + "\n"

        if help_string == "\n":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Выйти в главное меню"))
            bot.send_message(message.chat.id, "Вы еще не выбрали ни одного языка :(", reply_markup=markup)

        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # здесь нужен инлайн
            for i in range(len(split_user_languages)):
                if split_user_languages[i] == "🇬🇧 English":
                    item = types.KeyboardButton("English")
                    markup.add(item)
                if split_user_languages[i] == "🇩🇪 Deutsch":
                    item = types.KeyboardButton("Deutsch")
                    markup.add(item)
            item2 = types.KeyboardButton("/help")
            markup.add(item2)
            bot.send_message(message.chat.id, "Продолжам обучение! Выберите язык для продолжения обучения или help",
                             reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Введите /start")


@bot.message_handler(commands=['help'])
def help_message(message):
    # переопределить согласно логике
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchone()
    if record[0] != None:
        users_languages = get_languages(message.from_user.id)
        split_user_languages = re.split("&", users_languages)

        help_string = ""
        for i in range(0, len(split_user_languages)):
            help_string += split_user_languages[i] + "\n"

        if help_string == "\n":
            bot.send_message(message.chat.id,
                             "/new_language - добавляет новый язык\n/study - команда для продолжения изучения языков\n/remind - задает дни, в которые бот вас будет подгонять по учебе :)")
        elif (len(split_user_languages) == 2):
            bot.send_message(message.chat.id,
                             "/new_language - добавляет новый язык\n/study - команда для продолжения изучения языков\n/remind - задает дни, в которые бот вас будет подгонять по учебе :)")
            print(split_user_languages)
        elif (len(split_user_languages) == 3):
            bot.send_message(message.chat.id,
                             "/study - команда для продолжения изучения языков\n/remind - задает дни, в которые бот вас будет подгонять по учебе :)")
            print(split_user_languages)


# Выбор языков:
@bot.message_handler(commands=['new_language'])
def new_language_message(message):
    users_languages = get_languages(message.from_user.id)
    split_user_languages = re.split("&", users_languages)
    other_languages = languages
    # if the language is chosen, we don't create a button for it
    for i in range(0, len(split_user_languages)):
        if other_languages.__contains__(split_user_languages[i]):
            other_languages.remove(split_user_languages[i])
    # start creating buttons
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(other_languages)):
        # the actual creation of the button
        item = types.KeyboardButton(other_languages[i])
        markup.add(item)
    bot.send_message(message.chat.id, "Выберите язык", reply_markup=markup)


@bot.message_handler(commands=['remind'])
def remind_message(message):
    days = ["Понедельник🥱", "Вторник☹", "Среда😑", "Четверг🙂", "Пятница☺", "Суббота😎", "Воскресение🤪"]
    users_days = get_days(message.from_user.id)
    split_user_days = re.split("&", users_days)
    for i in range(0, len(split_user_days)):
        if days.__contains__(split_user_days[i]):
            days.remove(split_user_days[i])
    if days == []:
        bot.send_message(message.chat.id, "Вы и так уже занимаетесь каждый день!")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(0, len(days)):
            item = types.KeyboardButton(days[i])
            markup.add(item)
        bot.send_message(message.chat.id, "Выберите день недели", reply_markup=markup)


@bot.message_handler(commands=['vocab_eng'])
def add_to_eng_vocabulary(message):
    msg = bot.send_message(message.from_user.id,
                           "Запиши слово, которое хочешь добавить в словарь в таком формате: *слово* ")
    bot.register_next_step_handler(msg, after_text_2)


@bot.message_handler(commands=['vocab_deu'])
def add_to_deu_vocabulary(message):
    msg = bot.send_message(message.from_user.id,
                           "Запиши слово, которое хочешь добавить в словарь в таком формате: *слово* ")
    bot.register_next_step_handler(msg, after_text_1)


@bot.message_handler(commands=['get_eng_vocab'])
def get_eng_vocabe(message):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchall()
    for row in record:
        vocab_as_a_string = row[2]
    if vocab_as_a_string != None:
        vocab = vocab_as_a_string.split(",")
        file = Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)).touch()
        print(vocab)
        with open(Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)),
                  "w") as f:
            for i in range(len(vocab)):
                result = translator.translate(vocab[i])
                if vocab[i] == "":
                    continue
                else:
                    f.write(vocab[i] + " - " + result.text + "\n")
        file_to_send = open(Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)),
                            "r")
        bot.send_document(message.chat.id, file_to_send)
        file_to_send.close()
        Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)).unlink()
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Выйти в главное меню"))
        bot.send_message(message.chat.id, "Ваш словарь пуст :(", reply_markup=markup)


@bot.message_handler(commands=['get_deu_vocab'])
def get_deu_vocab(message):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchall()
    for row in record:
        vocab_as_a_string = row[3]
    if vocab_as_a_string != None:
        vocab = vocab_as_a_string.split(",")
        file = Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_deu.txt'.format(message.chat.id)).touch()
        print(vocab)
        with open(Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_deu.txt'.format(message.chat.id)),
                  "w") as f:
            for i in range(len(vocab)):
                result = translator.translate(vocab[i])
                if vocab[i] == "":
                    continue
                else:
                    f.write(vocab[i] + " - " + result.text + "\n")
        file_to_send = open(Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_deu.txt'.format(message.chat.id)),
                            "r")
        bot.send_document(message.chat.id, file_to_send)
        file_to_send.close()
        Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_deu.txt'.format(message.chat.id)).unlink()
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Выйти в главное меню"))
        bot.send_message(message.chat.id, "Ваш словарь пуст :(", reply_markup=markup)


@bot.message_handler(commands=['quiz_eng'])
def quiz_eng(message):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchall()
    for row in record:
        vocab_as_a_string = row[2]
    if vocab_as_a_string != None:
        vocab = vocab_as_a_string.split(",")[:-1]
        if len(vocab) < 4:

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Выйти в главное меню"))
            bot.send_message(message.chat.id, "Вы еще не набрали достаточное количество слов для квиза :(",
                             reply_markup=markup)
        else:
            words = random.sample(vocab, k=4)
            i = random.randint(0, 4)
            print(i)
            correct_word = translator.translate(words[i], src='en', dest='ru')
            # это для проверки после ввода пользователя
            print(words[i])
            global correct_word_in_russian_from_eng
            correct_word_in_russian_from_eng = correct_word.text
            # это для создания самого квиза, то есть по какому слову мы делаем квиз
            correct_word_in_english = words[i]
            # это для кнопок переводим слова
            translated_words = []
            for m in range(len(words)):
                result1 = translator.translate(words[m], src='en', dest='ru')
                translated_words.append(result1.text)

            markup = types.InlineKeyboardMarkup()
            for j in range(len(translated_words)):
                # the actual creation of the button
                if translated_words[j] == correct_word_in_russian_from_eng:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_right")
                else:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_wrong")
                markup.add(item)
            bot.send_message(message.chat.id, "Выберите перевод слова " + correct_word_in_english, reply_markup=markup)
            words = []
            translated_words = []
    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardBut % ton("Выйти в главное меню"))
        bot.send_message(message.chat.id, "Ваш словарь пуст :(", reply_markup=markup)


@bot.message_handler(commands=['quiz_deu'])
def quiz_deu(message):
    if vocab_as_a_string != None:
        info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
        record = info.fetchall()
        for row in record:
            vocab_as_a_string = row[3]
        vocab = vocab_as_a_string.split(",")[:-1]
        if len(vocab) < 4:

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardBut % ton("Выйти в главное меню"))
            bot.send_message(message.chat.id, "Вы еще не набрали достаточное количество слов для квиза :(",
                             reply_markup=markup)
        else:
            words = random.sample(vocab, k=4)
            i = random.randint(0, 4)
            print(i)
            correct_word = translator.translate(words[i], src='de', dest='ru')
            # это для проверки после ввода пользователя
            print(words[i])
            global correct_word_in_russian_from_deu
            correct_word_in_russian_from_deu = correct_word.text
            # это для создания самого квиза, то есть по какому слову мы делаем квиз
            correct_word_in_english = words[i]
            # это для кнопок переводим слова
            translated_words = []
            for m in range(len(words)):
                result1 = translator.translate(words[m], src='de', dest='ru')
                translated_words.append(result1.text)

            markup = types.InlineKeyboardMarkup()
            for j in range(len(translated_words)):
                # the actual creation of the button
                if translated_words[j] == correct_word_in_russian_from_deu:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_deu_right")
                else:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_deu_wrong")
                markup.add(item)
            bot.send_message(message.chat.id, "Выберите перевод слова " + correct_word_in_english, reply_markup=markup)
            words = []
            translated_words = []
    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardBut % ton("Выйти в главное меню"))
        bot.send_message(message.chat.id, "Ваш словарь пуст :(",
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def languages_handling(message):
    a = telebot.types.ReplyKeyboardRemove()
    if message.text == "Да eng":
        keyboard1 = types.InlineKeyboardMarkup()
        msg = bot.send_message(message.from_user.id,
                               "Запиши слово, которое хочешь добавить в словарь в таком формате: *слово* ")
        bot.register_next_step_handler(msg, after_text_2)
    # if message.text == "Вернуться в главное меню":
    #     #сюда бахнуть функционал стади
    if message.text == "Да deu":
        keyboard1 = types.InlineKeyboardMarkup()
        msg = bot.send_message(message.from_user.id,
                               "Запиши слово, которое хочешь добавить в словарь в таком формате: *слово* ")
        bot.register_next_step_handler(msg, after_text_1)
    if message.text == "Продолжить квиз на английском":
        info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
        record = info.fetchall()
        for row in record:
            vocab_as_a_string = row[2]
        vocab = vocab_as_a_string.split(",")[:-1]
        if len(vocab) < 4:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardBut % ton("Выйти в главное меню"))
            bot.send_message(message.chat.id, "Вы еще не набрали достаточное количество слов для квиза :(",
                             reply_markup=markup)
        else:
            words = random.sample(vocab, k=4)
            i = random.randint(0, 3)
            print(i)
            correct_word = translator.translate(words[i], src='en', dest='ru')
            # это для проверки после ввода пользователя
            print(words[i])

            correct_word_in_russian_from_eng = correct_word.text
            # это для создания самого квиза, то есть по какому слову мы делаем квиз
            correct_word_in_english = words[i]
            # это для кнопок переводим слова
            translated_words = []
            for m in range(len(words)):
                result1 = translator.translate(words[m], src='en', dest='ru')
                translated_words.append(result1.text)

            markup = types.InlineKeyboardMarkup()
            for j in range(len(translated_words)):
                # the actual creation of the button
                if translated_words[j] == correct_word_in_russian_from_eng:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_right")
                else:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_wrong")
                markup.add(item)
            bot.send_message(message.chat.id, "Выберите перевод слова " + correct_word_in_english, reply_markup=markup)
            words = []
            translated_words = []

    if message.text == "Продолжить квиз на немецком":
        info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
        record = info.fetchall()
        for row in record:
            vocab_as_a_string = row[3]
        vocab = vocab_as_a_string.split(",")[:-1]
        if len(vocab) < 4:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardBut % ton("Выйти в главное меню"))
            bot.send_message(message.chat.id, "Вы еще не набрали достаточное количество слов для квиза :(",
                             reply_markup=markup)
        else:
            words = random.sample(vocab, k=4)
            i = random.randint(0, 4)
            print(i)
            correct_word = translator.translate(words[i], src='de', dest='ru')
            # это для проверки после ввода пользователя
            print(words[i])
            global correct_word_in_russian_from_deu
            correct_word_in_russian_from_deu = correct_word.text
            # это для создания самого квиза, то есть по какому слову мы делаем квиз
            correct_word_in_english = words[i]
            # это для кнопок переводим слова
            translated_words = []
            for m in range(len(words)):
                result1 = translator.translate(words[m], src='de', dest='ru')
                translated_words.append(result1.text)

            markup = types.InlineKeyboardMarkup()
            for j in range(len(translated_words)):
                # the actual creation of the button
                if translated_words[j] == correct_word_in_russian_from_deu:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_deu_right")
                else:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_deu_wrong")
                markup.add(item)
            bot.send_message(message.chat.id, "Выберите перевод слова " + correct_word_in_english, reply_markup=markup)
            words = []
            translated_words = []
    if message.text == "Выйти в главное меню":
        info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
        record = info.fetchone()
        if record[0] != None:
            users_languages = get_languages(message.from_user.id)
            split_user_languages = re.split("&", users_languages)

            help_string = ""
            for i in range(0, len(split_user_languages)):
                help_string += split_user_languages[i] + "\n"

            if help_string == "\n":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton("Выйти в главное меню"))
                bot.send_message(message.chat.id, "Вы еще не выбрали ни одного языка :(", reply_markup=markup)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                # здесь нужен инлайн
                for i in range(len(split_user_languages)):
                    if split_user_languages[i] == "🇬🇧 English":
                        item = types.KeyboardButton("English")
                        markup.add(item)
                    if split_user_languages[i] == "🇩🇪 Deutsch":
                        item = types.KeyboardButton("Deutsch")
                        markup.add(item)
                item2 = types.KeyboardButton("/help")
                markup.add(item2)
                bot.send_message(message.chat.id, "Продолжам обучение! Выберите язык для продолжения обучения или help",
                                 reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Введите /start")

    if message.text == "Понедельник🥱" or message.text == "Вторник☹" or message.text == "Среда😑" or message.text == "Четверг🙂" \
            or message.text == "Пятница☺" or message.text == "Суббота😎" or message.text == "Воскресение🤪":
        str = message.text
        set_day(message.from_user.id, str)
        sqllite_db.connection.commit()
        newstr = str[:-1]
        if newstr == "Понедельник" or newstr == "Вторник" or newstr == "Четверг":
            bot.send_message(message.chat.id,
                             newstr + ' был добавлен в ваше расписание \n Чтобы продолжить обучение, жми /study',
                             reply_markup=a)
        if newstr == "Среда" or newstr == "Пятница" or newstr == "Суббота":
            bot.send_message(message.chat.id,
                             newstr + ' была добавлена в ваше расписание \n Чтобы продолжить обучение, жми /study',
                             reply_markup=a)
        if newstr == "Воскресение":
            bot.send_message(message.chat.id,
                             newstr + ' было добавлено в ваше расписание \n Чтобы продолжить обучение, жми /study',
                             reply_markup=a)
    if message.text == "🇬🇧 English":
        str = "🇬🇧 English"
        bot.send_message(message.chat.id, 'Now you are a englishman \n Чтобы продолжить обучение, жми /study',
                         reply_markup=a)
        set_language(message.from_user.id, str)
        sqllite_db.connection.commit()


    elif message.text == "🇩🇪 Deutsch":
        str = "🇩🇪 Deutsch"
        bot.send_message(message.chat.id, 'Jetzt du bist Deutsch Person \n Чтобы продолжить обучение, жми /study',
                         reply_markup=a)
        set_language(message.from_user.id, str)
        sqllite_db.connection.commit()
    if message.text == "English":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/quiz_eng")
        markup.add(item)
        item = types.KeyboardButton("/get_eng_vocab")
        markup.add(item)
        item2 = types.KeyboardButton("/vocab_eng")
        markup.add(item2)
        bot.send_message(message.chat.id, "Что вы хотите сделать?",
                         reply_markup=markup)
    if message.text == "Deutsch":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/quiz_deu")
        markup.add(item)
        item = types.KeyboardButton("/get_deu_vocab")
        markup.add(item)
        item2 = types.KeyboardButton("/vocab_deu")
        markup.add(item2)
        bot.send_message(message.chat.id, "Что вы хотите сделать?",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'quiz_eng_right')
def send_study(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Продолжить квиз на английском")
    markup.add(item)
    item = types.KeyboardButton("Выйти в главное меню")
    markup.add(item)
    bot.send_message(call.message.chat.id, 'Правильно! Если хочешь продолжить квиз, жми продолжить.',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'quiz_eng_wrong')
def send_study(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Продолжить квиз на английском")
    markup.add(item)
    item = types.KeyboardButton("Выйти в главное меню")
    markup.add(item)
    bot.send_message(call.message.chat.id,
                     'Неправильно! Правильный перевод ' + correct_word_in_russian_from_eng + '. Если хочешь продолжить квиз, жми продолжить.',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'quiz_deu_wrong')
def send_study(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Продолжить квиз на немецком")
    markup.add(item)
    item = types.KeyboardButton("Выйти в главное меню")
    markup.add(item)
    bot.send_message(call.message.chat.id,
                     'Неправильно! Правильный перевод ' + correct_word_in_russian_from_deu + '. Если хочешь продолжить квиз, жми продолжить.',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'quiz_deu_right')
def send_study(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Продолжить квиз на немецком")
    markup.add(item)
    item = types.KeyboardButton("Выйти в главное меню")
    markup.add(item)
    bot.send_message(call.message.chat.id, 'Правильно! Если хочешь продолжить квиз, жми продолжить.',
                     reply_markup=markup)


# ----------------------------------------------------------
def start_process():  # Запуск Process
    multiprocessing.Process(target=P_schedule.start_schedule, args=()).start()


class P_schedule():  # Class для работы с schedule
    def start_schedule():  # Запуск schedule
        ######Параметры для schedule######
        schedule.every().day.at("09:00").do(P_schedule.send_message1)
        schedule.every().day.at("16:00").do(P_schedule.send_message1)
        schedule.every().day.at("22:00").do(P_schedule.send_message1)
        ##################################

        while True:  # Запуск цикла
            schedule.run_pending()
            time.sleep(1)

    ####Функции для выполнения заданий по времени
    def send_message1():
        days = ["Понедельник🥱", "Вторник☹", "Среда😑", "Четверг🙂", "Пятница☺", "Суббота😎", "Воскресение🤪"]
        currentDay = datetime.datetime.today().weekday()
        info = sqllite_db.cursor.execute('SELECT user_id, days FROM users')
        record = info.fetchall()
        currentDay_text = days[currentDay]
        print(currentDay_text)
        for i in range(0, len(record)):
            weekdays = record[i]
            id = weekdays[0]
            day = weekdays[1]
            split_user_days = re.split("&", day)
            for j in range(0, len(split_user_days)):
                if split_user_days[j] == currentDay_text:
                    if datetime.datetime.today().time().hour == 14:
                        nine(id)
                    if datetime.datetime.today().time().hour == 14:
                        four(id)
                    if datetime.datetime.today().time().hour == 14:
                        ten(id)
    ################


if __name__ == '__main__':
    start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
