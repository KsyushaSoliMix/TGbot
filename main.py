# Библиотеки
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
   (user_id, name, languages)
VALUES (?, ?, ?);"""
# ----------------------------------------------------------

my_languages = []



@bot.message_handler(commands=['start'])
def start_message(message):
    # Создаем нового юзера и добавляем его в базу данных, с проверкой на то, был ли он до этого зарегестрирован
    info = sqllite_db.cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    if info.fetchone() is None:
        bot.send_message(message.chat.id, "Привет " + message.from_user.first_name + "!\n" \
                                                                                     "Study language bot поможет тебе в изучении разных иностранных языков.\n" \
                                                                                     "Введи /help для того, чтобы посмотреть функционал.")
        person_data = (message.from_user.id, message.from_user.first_name, "")
        sqllite_db.cursor.execute(create_users, person_data)
        sqllite_db.connection.commit()
    else:
        bot.send_message(message.chat.id, "Привет " + message.from_user.first_name + "! Готов продолжить обучение?\n Вводи команду /study и поехали!!!")

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, help_line)


# Выбор языков:
@bot.message_handler(commands=['new_language'])
def new_language_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(languages)):
        item = types.KeyboardButton(languages[i])
        markup.add(item)
    bot.send_message(message.chat.id, "Выберите язык", reply_markup=markup)


@bot.message_handler(commands=['my_languages'])
def get_my_languages_message(message):
    help_string = ""
    for i in range(0, len(my_languages)):
        help_string += my_languages[i] + "\n"
    if help_string == "":
        bot.send_message(message.chat.id, "Вы еще не выбрали ни одного языка :(")
    else:
        bot.send_message(message.chat.id, help_string)


@bot.message_handler(content_types=['text'])
def languages_handling(message):
    a = telebot.types.ReplyKeyboardRemove()
    if message.text == "🇬🇧 English":
        str = "🇬🇧 English"
        languages.remove(str)
        bot.send_message(message.chat.id, 'Now you are a englishman', reply_markup=a)
        my_languages.append(str)
    elif message.text == "🇩🇪 Deutsch":
        str = "🇩🇪 Deutsch"
        languages.remove(str)
        bot.send_message(message.chat.id, 'Jetzt du bist Deutsch Person', reply_markup=a)
        my_languages.append(str)
    elif message.text == "🇷🇺 Русский":
        bot.send_message(message.chat.id, 'Уйди отсюда, пидор грязный')


# ----------------------------------------------------------
bot.polling(none_stop=True)
