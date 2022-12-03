import sys

sys.path.append('../eureka')
import telebot
from telebot import types
from project.config_files.config import TELEGRAM_TOKEN

# for testing: https://t.me/eurekachatbot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

sites_list = [["Parks", "Public Gardens", "City Walls"], ["Churches"]] #TODO: add more items

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello {}! I'm {} and I can help you to discover cultural assets in Pisa.".format(message.chat.first_name, "EUREKA"))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Parks"), types.KeyboardButton("Public Garden"), types.KeyboardButton("City Walls"))
    keyboard.add(types.KeyboardButton("Churches"))
    bot.send_message(message.chat.id, "What would you like to visit?", reply_markup=keyboard)

#text handling
@bot.message_handler(content_types=['text'])
def text_handling(message):
    pass


bot.infinity_polling()