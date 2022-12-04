import sys
sys.path.append('../eureka')
import telebot
from telebot import types
from project.config_files.config import TELEGRAM_TOKEN
from utilities import *

# for testing: https://t.me/eurekachatbot
bot = telebot.TeleBot(TELEGRAM_TOKEN)



# conversation flow
@bot.message_handler(commands=['start'])
def handle_conversation(message):
    bot.send_message(message.chat.id, "Hello {}! I'm {} and I can help you to discover cultural assets in Pisa.".format(message.chat.first_name, "EUREKA"))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    bot.send_message(message.chat.id, "What would you like to do?", reply_markup=keyboard)
    bot.register_next_step_handler(message, create_keyboard(keyboard))
    bot.register_next_step_handler(message, greetings)

def greetings(message):
    bot.send_message(message.chat.id, "Ok, bye")

#text handling
@bot.message_handler(content_types=['text'])
def text_handling(message):
    pass


#bot.enable_save_next_step_handlers(delay=1)
#bot.load_next_step_handlers()
bot.infinity_polling()