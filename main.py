# Библиотеки
import telebot
from telebot import types

# Токен и создание бота
token = '5305392177:AAGRLxjBJ43TgZSo7qC8XoXRJ75bKCzh7Fk'
bot = telebot.TeleBot(token)
# ----------------------------------------------------------

# Переменные для команд

languages = "🇬🇧 English", "🇩🇪 Deutsch", "🇷🇺 Русский"

help_line = "/newLanguage - добавляет новый язык.\n" \
            "/study *язык* - команда для продолжения изучения языка."


# ----------------------------------------------------------


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет " + message.from_user.first_name  +"!\n" \
             "Study language bot поможет тебе в изучении разных иностранных языков.\n" \
             "Введи /help для того, чтобы посмотреть функционал.")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, help_line)


# Выбор языков:
@bot.message_handler(commands=['newLanguage'])
def new_language_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(languages)):
        item = types.KeyboardButton(languages[i])
        markup.add(item)
    bot.send_message(message.chat.id, "Выберите язык", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def languages_handling(message):
    if (message.text == "🇬🇧 English"):
        bot.send_message(message.chat.id, 'Now you are a englishman')
    elif (message.text == "🇩🇪 Deutsch"):
        bot.send_message(message.chat.id, 'Jetzt du bist Deutsch Person')
    elif (message.text == "🇷🇺 Русский"):
        bot.send_message(message.chat.id, 'Уйди отсюда, пидор грязный')

# ----------------------------------------------------------
bot.polling(none_stop=True)
