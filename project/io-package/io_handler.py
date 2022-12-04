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

    #TODO: add more items
    sites_list = ["Parks", "Public Gardens", "City Walls", "Churches", "Squares", "Museums", "Monuments" ] # "Cultural Events"
    create_keyboard(keyboard, sites_list)
    #TODO: handle unknown input
    msg = bot.send_message(message.chat.id, "What would you like to do?", reply_markup=keyboard) #TODO: fix question
    bot.register_next_step_handler(msg, site_label_handler)

# STEP 1: the user choice is handled
def site_label_handler(message):
    site_label = convert_to_label(message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    labels = ["Accessibility", "Prices", "Rating"]
    create_keyboard(keyboard, labels)
    keyboard.add(types.KeyboardButton("Show me results")) # Make this button separeted from the group
    msg = bot.send_message(message.chat.id, "I can improve the search if you suggest other details or show you the results for ""{}".format(message.text), reply_markup=keyboard)
    bot.register_next_step_handler(msg, search_improvements_handler)

# STEP 2: check if user wants to add more details to the query. If not the bot shows query results
def search_improvements_handler(message):
    if message.text == "Accessibility":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        labels = ["Yes", "No"]
        create_keyboard(keyboard, labels)
        keyboard.add(types.KeyboardButton("< Back"))
        msg = bot.send_message(message.chat.id, "Are you in a wheelchair?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)
    elif message.text == "Prices":
        pass
    elif message.text == "Rating":
        pass
    elif message.text == "Show me results":
        pass
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        labels = ["Accessibility", "Prices", "Rating"]
        create_keyboard(keyboard, labels)
        keyboard.add(types.KeyboardButton("Show me results"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

# STEP 2.1: checks whether the user is in a wheelchair 
def accessibility_choice_handler(message):
    if message.text == "Yes":
        #TODO: save user choice
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        labels = ["Prices", "Rating"]
        create_keyboard(keyboard, labels)
        keyboard.add(types.KeyboardButton("Show me results"))

        msg = bot.send_message(message.chat.id, "Want to add more?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)
    elif message.text == "No":
        #TODO: save user choice
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        labels = ["Prices", "Rating"]
        create_keyboard(keyboard, labels)
        keyboard.add(types.KeyboardButton("Show me results"))

        msg = bot.send_message(message.chat.id, "Want to add more?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)
        pass
    elif message.text == "< Back":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        labels = ["Accessibility", "Prices", "Rating"]
        create_keyboard(keyboard, labels)
        keyboard.add(types.KeyboardButton("Show me results"))

        msg = bot.send_message(message.chat.id, "I can improve the search or show you the results. What I can do?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        labels = ["Yes", "No"]
        create_keyboard(keyboard, labels)
        keyboard.add(types.KeyboardButton("< back"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)


bot.infinity_polling()