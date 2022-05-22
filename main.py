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

# Токен и создание бота

token = '5305392177:AAGRLxjBJ43TgZSo7qC8XoXRJ75bKCzh7Fk'
bot = telebot.TeleBot(token)

# ----------------------------------------------------------

# Переменные для команд

translator = Translator()

languages = ["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇺 Русский"]


create_users = """
INSERT INTO users 
   (user_id, languages,vocabulary_eng, vocabulary_deu)
VALUES (?, ?, ?, ?);"""

# ----------------------------------------------------------

correct_word_in_russian=''

# Функции для получения и сохранения языков:
def get_languages(user_id):

    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    record = info.fetchone()
    return record[1]


def set_language(user_id, language):

    help_language = get_languages(user_id) + language + "&"
    sqllite_db.cursor.execute('UPDATE users SET languages = ? WHERE user_id = ?', (help_language, user_id))
    sqllite_db.connection.commit()


#сюда закидывается слово из vocab_eng
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
    #здесь нужен инлайн
    item1 = types.KeyboardButton("Да")
    markup.add(item1)
    item1 = types.KeyboardButton("Выйти в главное меню")
    markup.add(item1)
    bot.send_message(message.chat.id,"Продолжить добавлять слова?",reply_markup=markup)



# ----------------------------------------------------------


@bot.message_handler(commands=['start'])
def start_message(message):
    # Создаем нового юзера и добавляем его в базу данных, с проверкой на то, был ли он до этого зарегестрирован
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))

    info.fetchone()
    if info.fetchone() is None:
        bot.send_message(message.chat.id, "Привет, " + message.from_user.first_name + "!\n" \
                                                                                     "Study language bot поможет тебе в изучении разных иностранных языков.\n" \
                                                                                     "Введи /help для того, чтобы посмотреть функционал.")

        person_data = (message.from_user.id, "", None,None)
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
            bot.send_message(message.chat.id, "Вы еще не выбрали ни одного языка :(")
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # здесь нужен инлайн
            for i in range(len(split_user_languages)):
                if split_user_languages[i]=="🇬🇧 English":
                    item = types.KeyboardButton("English")
                    markup.add(item)
                if split_user_languages[i]=="🇩🇪 Deutsch":
                    item = types.KeyboardButton("Deutsch")
                    markup.add(item)
            item2 = types.KeyboardButton("/help")
            markup.add(item2)
            bot.send_message(message.chat.id, "Продолжам обучение! Выберите язык для продолжения обучения или help", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Введите /start")


@bot.message_handler(commands=['help'])
def help_message(message):
    #переопределить согласно логике
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchone()
    if record[0] != None:
        users_languages = get_languages(message.from_user.id)
        split_user_languages = re.split("&", users_languages)

        help_string = ""
        for i in range(0, len(split_user_languages)):
            help_string += split_user_languages[i] + "\n"

        if help_string == "\n":
            bot.send_message(message.chat.id, "/new_language - добавляет новый язык\n/study - команда для продолжения изучения языков\n/remind - задает дни, в которые бот вас будет подгонять по учебе :)")
        elif (len(split_user_languages)==2):
            bot.send_message(message.chat.id,
                             "/new_language - добавляет новый язык\n/study - команда для продолжения изучения языков\n/remind - задает дни, в которые бот вас будет подгонять по учебе :)")
            print(split_user_languages)
        elif (len(split_user_languages)==3):
            bot.send_message(message.chat.id,
                             "/study - команда для продолжения изучения языков\n/remind - задает дни, в которые бот вас будет подгонять по учебе :)")
            print(split_user_languages)



# Выбор языков:
@bot.message_handler(commands=['new_language'])
def new_language_message(message):

    users_languages = get_languages(message.from_user.id)
    split_user_languages = re.split("&", users_languages)
    other_languages = languages
    #if the language is chosen, we don't create a button for it
    for i in range(0, len(split_user_languages)):
        if other_languages.__contains__(split_user_languages[i]):
            other_languages.remove(split_user_languages[i])
    #start creating buttons
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(other_languages)):
        #the actual creation of the button
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




@bot.message_handler(commands=['vocab_eng'])
def add_to_eng_vocabulary(message):


        msg = bot.send_message(message.from_user.id, "Запиши слово, которое хочешь добавить в словарь в таком формате: *слово* ")
        bot.register_next_step_handler(msg, after_text_2)




@bot.message_handler(commands=['get_eng_vocab'])
def new_language_message(message):
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    record = info.fetchall()
    for row in record:
        vocab_as_a_string = row[2]
    if vocab_as_a_string!=None:
        vocab = vocab_as_a_string.split(",")
        file = Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)).touch()
        print(vocab)
        with open(Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)),"w") as f:
            for i in range(len(vocab)):
                result = translator.translate(vocab[i])
                if vocab[i]=="":
                    continue
                else:
                    f.write(vocab[i] + " - " + result.text + "\n")
        file_to_send = open(Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)), "r")
        bot.send_document(message.chat.id, file_to_send)
        file_to_send.close()
        Path('C:\\Users\\Natasha\\PycharmProjects\\TGbot_orig\\{}_eng.txt'.format(message.chat.id)).unlink()
    else:
        bot.send_message(message.from_user.id,
                         "Ваш словарь пуст :(")

@bot.message_handler(commands=['quiz_eng'])
def new_language_message(message):
    if vocab_as_a_string != None:
        info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
        record = info.fetchall()
        for row in record:
            vocab_as_a_string = row[2]
        vocab = vocab_as_a_string.split(",")[:-1]
        if len(vocab)<4:
            bot.send_message(message.chat.id, "Вы еще не набрали достаточное количество слов для квиза :(")
        else:
            words = random.sample(vocab, k=4)
            i = random.randint(0,4)
            print(i)
            correct_word = translator.translate(words[i],  src='en', dest='ru')
            #это для проверки после ввода пользователя
            print(words[i])
            global correct_word_in_russian
            correct_word_in_russian = correct_word.text
            #это для создания самого квиза, то есть по какому слову мы делаем квиз
            correct_word_in_english = words[i]
            #это для кнопок переводим слова
            translated_words = []
            for m in range(len(words)):
                result1 = translator.translate(words[m], src='en', dest='ru')
                translated_words.append(result1.text)
            print(translated_words)
            print(correct_word_in_russian)
            markup = types.InlineKeyboardMarkup()
            for j in range(len(translated_words)):
                # the actual creation of the button
                if translated_words[j]==correct_word_in_russian:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_right")
                else:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_wrong")
                markup.add(item)
            bot.send_message(message.chat.id, "Выберите перевод слова "+correct_word_in_english, reply_markup=markup)
            words=[]
            translated_words=[]
    else:
        bot.send_message(message.chat.id, "Ваш словарь пуст :(")


@bot.message_handler(content_types=['text'])
def languages_handling(message):
    a = telebot.types.ReplyKeyboardRemove()
    if message.text == "Да":
        keyboard1 = types.InlineKeyboardMarkup()
        msg = bot.send_message(message.from_user.id,
                               "Запиши слово, которое хочешь добавить в словарь в таком формате: *слово* ")
        bot.register_next_step_handler(msg, after_text_2)
    # if message.text == "Вернуться в главное меню":
    #     #сюда бахнуть функционал стади
    if message.text=="Продолжить квиз":
        info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
        record = info.fetchall()
        for row in record:
            vocab_as_a_string = row[2]
        vocab = vocab_as_a_string.split(",")[:-1]
        if len(vocab) < 4:
            bot.send_message(message.chat.id, "Вы еще не набрали достаточное количество слов для квиза :(")
        else:
            words = random.sample(vocab, k=4)
            i = random.randint(0, 3)
            print(i)
            correct_word = translator.translate(words[i], src='en', dest='ru')
            # это для проверки после ввода пользователя
            print(words[i])

            correct_word_in_russian = correct_word.text
            # это для создания самого квиза, то есть по какому слову мы делаем квиз
            correct_word_in_english = words[i]
            # это для кнопок переводим слова
            translated_words = []
            for m in range(len(words)):
                result1 = translator.translate(words[m], src='en', dest='ru')
                translated_words.append(result1.text)
            print(translated_words)
            print(correct_word_in_russian)
            markup = types.InlineKeyboardMarkup()
            for j in range(len(translated_words)):
                # the actual creation of the button
                if translated_words[j] == correct_word_in_russian:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_right")
                else:
                    item = types.InlineKeyboardButton(text=translated_words[j], callback_data="quiz_eng_wrong")
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
                bot.send_message(message.chat.id, "Вы еще не выбрали ни одного языка :(")
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

    if message.text == "🇬🇧 English":
        str = "🇬🇧 English"
        bot.send_message(message.chat.id, 'Now you are a englishman \n Чтобы продолжить обучение, жми /study', reply_markup=a)
        set_language(message.from_user.id, str)
        sqllite_db.connection.commit()


    elif message.text == "🇩🇪 Deutsch":
        str = "🇩🇪 Deutsch"
        bot.send_message(message.chat.id, 'Jetzt du bist Deutsch Person \n Чтобы продолжить обучение, жми /study', reply_markup=a)
        set_language(message.from_user.id, str)
        sqllite_db.connection.commit()
    if message.text=="English":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/quiz_eng")
        markup.add(item)
        item = types.KeyboardButton("/get_eng_vocab")
        markup.add(item)
        item2 = types.KeyboardButton("/vocab_eng")
        markup.add(item2)
        bot.send_message(message.chat.id, "Что вы хотите сделать?",
                         reply_markup=markup)
    if message.text=="Deutsch":
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
    item = types.KeyboardButton("Продолжить квиз")
    markup.add(item)
    item = types.KeyboardButton("Выйти в главное меню")
    markup.add(item)
    bot.send_message(call.message.chat.id, 'Правильно! Если хочешь продолжить квиз, жми продолжить.', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'quiz_eng_wrong')
def send_study(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Продолжить квиз")
    markup.add(item)
    item = types.KeyboardButton("Выйти в главное меню")
    markup.add(item)
    bot.send_message(call.message.chat.id, 'Неправильно! Правильный перевод '+correct_word_in_russian+'. Если хочешь продолжить квиз, жми продолжить.',
                     reply_markup=markup)
# ----------------------------------------------------------
bot.polling(none_stop=True)
