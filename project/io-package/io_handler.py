import os
import re
import sys
import swiplserver

subdir = re.sub("eureka.*","eureka",os.getcwd())
os.chdir(subdir)
sys.path.append('../eureka')

import telebot
from project.config_files.config import TELEGRAM_TOKEN
from project.bot_backend.utilities import *

# for testing: https://t.me/eurekachatbot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

query_parameters = {
    "fact": "",
    "ID": "Id",
    "label": "Label",
    "lat": "",
    "lon":"",
    "accessibility": "",
    "tripadvisor_id": "",
    "image" : "",
    "stars": ""
}


#TODO: add more items
sites_list = ["Parks", "Public Gardens", "City Walls", "Churches", "Squares", "Museums", "Monuments" ] # "Cultural Events"

search_improvement_list = ["Accessibility", "Rating", "Prices"]

ORIGINAL_DIM_SEARCH_IMPROVEMENT = len(search_improvement_list)
 #STEP 0: bot is started and asks user to choose an asset category (Arts & Culture, Architecture, Green Areas)
@bot.message_handler(commands=['start'])
def handle_conversation(message):
    bot.send_message(message.chat.id, "Hello {}! I'm {} and I can help you to discover cultural assets in Pisa.".format(message.chat.first_name, "EUREKA"))

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) 
    create_keyboard(keyboard, ["Arts & Culture", "Architecture", "Green Areas"])
    msg = bot.send_message(message.chat.id, "Let's start by choosing a category", reply_markup=keyboard)
    bot.register_next_step_handler(msg, category_handler)

#STEP 0.1: bot asks user to select a sub-category (churches, monuments, towers, etc.)
def category_handler(message):
    if message.text == "Arts & Culture":

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        #TODO: fill the keyboard with remaining item
        create_keyboard(keyboard, ["Museums"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Great!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)
    elif message.text == "Architecture":

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["City Walls", "Churches", "Squares", "Monuments"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Great!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)
    elif message.text == "Green Areas":

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Parks", "Public Gardens"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Great!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)
    else:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Arts & Culture", "Architecture", "Green Areas"])

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, category_handler)


# STEP 1: the user choice is handled
def site_label_handler(message):

    #if the message is a sub-category (churches, monuments, towers, etc.)
    if message.text in sites_list:
        #TODO
        query_parameters["fact"] = convert_to_label(message.text)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Accessibility", "Prices", "Rating"])
        # Make this button separated from the group
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I can improve the search if you suggest other details or show you the results for {}".format(message.text), reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "< Back":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Arts & Culture", "Architecture", "Green Areas"])

        msg = bot.send_message(message.chat.id, "To start, choose a category below", reply_markup=keyboard)
        bot.register_next_step_handler(msg, category_handler)

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) 
        create_keyboard(keyboard, sites_list)

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)

# STEP 2: check if user wants to add more details to the query (accessibility, cost, rating etc.). If not, the bot shows query results
def search_improvements_handler(message):

    global search_improvement_list
    # if the message is a request for details
    if message.text == "Accessibility":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Yes", "No"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Are you in a wheelchair?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)

    #TODO
    elif message.text == "Prices":
        pass
   #TODO now
    elif message.text == "Rating":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["⭐", "⭐⭐", "⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Choose the rating!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)
    elif message.text == "Show me results":
        pass

    elif message.text == "< Back":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        if len(search_improvement_list) == ORIGINAL_DIM_SEARCH_IMPROVEMENT:
            create_keyboard(keyboard, ["Arts & Culture", "Architecture", "Green Areas"])
            #keyboard.add(types.KeyboardButton("< Back"))
            msg = bot.send_message(message.chat.id, "To start, choose a category below", reply_markup=keyboard)
            bot.register_next_step_handler(msg, category_handler)
        else:
            search_improvement_list = ["Accessibility", "Prices", "Rating"]
            create_keyboard(keyboard, search_improvement_list)
            keyboard.add(types.KeyboardButton("< Back"))
            keyboard.add(types.KeyboardButton("Show me results"))

            msg = bot.send_message(message.chat.id, "I can improve the search or show you the results. What can I do?",
                                   reply_markup=keyboard)
            bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Accessibility", "Prices", "Rating"])
        keyboard.add(types.KeyboardButton("Show me results"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

# STEP 2.1: checks whether the user is in a wheelchair 
def accessibility_choice_handler(message):

    global search_improvement_list

    if message.text == "Yes":
        #TODO: save user choice
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list.remove("Accessibility")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "No":
        #TODO: save user choice
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list.remove("Accessibility")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "< Back":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list = ["Accessibility", "Prices", "Rating"]
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I can improve the search or show you the results. What can I do?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Yes", "No"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)

#TODO
# STEP 2.2: checks user's price preferences about cultural assets
def prices_choice_handler(message):
    pass

# STEP 2.3: checks user's preferences about assets rating
def rating_choice_handler(message):

    global search_improvement_list
    if message.text == "⭐":
        #TODO: save user choice
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "⭐⭐":
        #TODO: save user choice
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "⭐⭐⭐":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "⭐⭐⭐⭐":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "⭐⭐⭐⭐⭐":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "< Back":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        search_improvement_list = ["Accessibility", "Prices", "Rating"]
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I can improve the search or show you the results. What can I do?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["⭐", "⭐⭐", "⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)

# Show query results
def show_results(message):
    # TODO: prolog query to kb
    pass


def back_button_handler(message):

    create_keyboard()

bot.infinity_polling()