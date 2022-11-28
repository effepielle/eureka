import telebot
from project.dialogflow_api import nlp_handler as nlp
from project.config_files.config import TELEGRAM_TOKEN

# for testing: https://t.me/eurekachatbot
bot = telebot.TeleBot(TELEGRAM_TOKEN)


'''
boilerplate for default command handling
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello world")
'''

#text handling
@bot.message_handler(content_types=['text'])
def handle_NL_text(message):
    # TODO:

    # if we want to pass it to df module
     out = nlp.analyze_input(message.chat.id, message.text)
     bot.send_message(message.chat.id, out)

    # else we want to process locally message without df module NLP processing
    # out = process_costum_input(session_id, message)
    # bot.send_message(message.chat.id, out)


bot.infinity_polling()