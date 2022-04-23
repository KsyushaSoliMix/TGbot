import telebot

token = '5305392177:AAGRLxjBJ43TgZSo7qC8XoXRJ75bKCzh7Fk'
bot = telebot.TeleBot(token)


start_line = "Привет ✌ \n" \
             "Study language bot поможет тебе в изучении разных иностранных языков.\n" \
             "Введи /help для того, чтобы посмотреть функционал."

languages = "English\n"

help_line = "/newLanguage *ваш язык для изучения* - добавляет новый язык. Доступные языки:\n" + languages +\
            "/study *язык* - команда для продолжения изучения языка."


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, start_line)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, help_line)


@bot.message_handler(commands=['newLanguage'])
def newLanguage_message(message):
    bot.send_message(message.chat.id, help_line)


@bot.message_handler(content_types=['text'])
def hello(message):
    if message.text == "Hello":
      bot.send_message(message.chat.id, message.text)
    elif message.text == "Привет":
      bot.send_message(message.chat.id, "Ненавижу глупых русских!!!")

bot.polling(none_stop=True)
