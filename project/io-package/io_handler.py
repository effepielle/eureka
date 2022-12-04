import sys
import os
import re

subdir = re.sub("eureka.*","eureka",os.getcwd())
os.chdir(subdir)
sys.path.append('../eureka/project')

import telebot
from telebot import types
#from project.config_files.config import TELEGRAM_TOKEN
from backend.utilities import *

# for testing: https://t.me/eurekachatbot
bot = telebot.TeleBot('5689759624:AAHfrWL9xPd8KlG11ah1wm95EMago4TK6AI') #TODO: fix token path
 
 #STEP 0: bot is started and asks user to choose an asset type (churches, monuments, towers, etc.)
@bot.message_handler(commands=['start'])
def handle_conversation(message):
    bot.send_message(message.chat.id, "Hello {}! I'm {} and I can help you to discover cultural assets in Pisa.".format(message.chat.first_name, "EUREKA"))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) 
    create_keyboard(keyboard)
    msg = bot.send_message(message.chat.id, "What would you like to do?", reply_markup=keyboard) #TODO: fix question
    bot.register_next_step_handler(msg, site_label_handler)

# STEP 1: the user choice is handled
def site_label_handler(message):
    print(message.text)

bot.infinity_polling()