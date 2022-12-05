import os
import re
import sys

import pandas as pd
import swiplserver
from swiplserver import PrologMQI

subdir = re.sub("eureka.*", "eureka", os.getcwd())
os.chdir(subdir)
sys.path.append('../eureka')

import telebot
from telebot import types
from project.config_files.config import TELEGRAM_TOKEN, IMAGE_PLACEHOLDER
from project.bot_backend.utilities import *
import numpy as np


query_parameters = {
    "fact": "",
    "ID": "Id",
    "label": "Label",
    "lat": "Lat",
    "lon": "Long",
    "accessibility": "_",
    "tripadvisor_id": "TripID",
    "image": "Image",
    "stars": "Star"
}

#contains the final query results. It needs to be here to be visible to callback query handler methods
main_query_results = None

# TODO: add more items
sites_list = ["Parks", "Public Gardens", "City Walls", "Churches", "Squares", "Museums",
              "Monuments"]  # "Cultural Events"

search_improvement_list = ["Accessibility", "Rating", "Prices"]

ORIGINAL_DIM_SEARCH_IMPROVEMENT = len(search_improvement_list)


# for testing: https://t.me/eurekachatbot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# STEP 0: bot is started and asks user to choose an asset category (Arts & Culture, Architecture, Green Areas)
@bot.message_handler(commands=['start'])
def handle_conversation(message):
    global search_improvement_list
    global query_parameters

    bot.send_message(message.chat.id, "Hello {}! I'm {} and I can help you to discover cultural assets in Pisa.".format(
        message.chat.first_name, "EUREKA"))

    search_improvement_list = ["Accessibility", "Rating", "Prices"]
    query_parameters = {
    "fact": "",
    "ID": "Id",
    "label": "Label",
    "lat": "Lat",
    "lon": "Long",
    "accessibility": "_",
    "tripadvisor_id": "TripID",
    "image": "Image",
    "stars": "Star"
}

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    create_keyboard(keyboard, ["Arts & Culture", "Architecture", "Green Areas"])
    msg = bot.send_message(message.chat.id, "Let's start by choosing a category", reply_markup=keyboard)
    bot.register_next_step_handler(msg, category_handler)


# STEP 0.1: bot asks user to select a sub-category (churches, monuments, towers, etc.)
def category_handler(message):
    if message.text == "Arts & Culture":

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        # TODO: fill the keyboard with remaining item
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

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, category_handler)


# STEP 1: the user choice is handled
def site_label_handler(message):
    # if the message is a sub-category (churches, monuments, towers, etc.)
    if message.text in sites_list:
        # TODO
        query_parameters["fact"] = convert_to_label(message.text)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Accessibility", "Prices", "Rating"])
        # In this way you can separate Show results and back buttons from the rest of the group
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id,
                               "I can improve the search if you suggest other details or show you the results for {}".format(
                                   message.text), reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "< Back":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["Arts & Culture", "Architecture", "Green Areas"])

        msg = bot.send_message(message.chat.id, "To start, choose a category below", reply_markup=keyboard)
        bot.register_next_step_handler(msg, category_handler)

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, sites_list)

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)


# STEP 2: check if user wants to add more details to the query (accessibility, cost, rating etc.). If not,
# the bot shows query results
def search_improvements_handler(message):
    global search_improvement_list
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    # if the message is a request for details
    if message.text == "Accessibility":
        create_keyboard(keyboard, ["Yes", "No"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Are you in a wheelchair?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)

    # TODO
    elif message.text == "Prices":
        pass

    elif message.text == "Rating":
        create_keyboard(keyboard, ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Choose the rating!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)


    elif message.text == "Show me results":
        show_results_handler(message)

    elif message.text == "< Back":

        if len(search_improvement_list) == ORIGINAL_DIM_SEARCH_IMPROVEMENT:
            create_keyboard(keyboard, ["Arts & Culture", "Architecture", "Green Areas"])
            # TODO keyboard.add(types.KeyboardButton("< Back"))
            msg = bot.send_message(message.chat.id, "To start, choose a category below", reply_markup=keyboard)
            bot.register_next_step_handler(msg, category_handler)

        else:
            search_improvement_list = ["Accessibility", "Prices", "Rating"]
            create_keyboard(keyboard, search_improvement_list)
            keyboard.add(types.KeyboardButton("Show me results"))
            keyboard.add(types.KeyboardButton("< Back"))

            msg = bot.send_message(message.chat.id, "I can improve the search or show you the results. What can I do?",
                                   reply_markup=keyboard)
            bot.send_message(message.chat.id, generate_search_improvement_choices(query_parameters))
            bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        create_keyboard(keyboard, ["Accessibility", "Prices", "Rating"])
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


# STEP 2.1: checks whether the user is in a wheelchair
def accessibility_choice_handler(message):

    global search_improvement_list
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)


    if message.text == "Yes":
        query_parameters["accessibility"] = "wheelchair accessible"

        search_improvement_list.remove("Accessibility")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "No":
        query_parameters["accessibility"] = np.nan
        search_improvement_list.remove("Accessibility")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "< Back":
        search_improvement_list = ["Accessibility", "Prices", "Rating"]
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I can improve the search or show you the results. What can I do?",
                               reply_markup=keyboard)
        bot.send_message(message.chat.id, generate_search_improvement_choices(query_parameters))
        bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        create_keyboard(keyboard, ["Yes", "No"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)


# TODO
# STEP 2.2: checks user's price preferences about cultural assets
def prices_choice_handler(message):
    pass


# STEP 2.3: checks user's preferences about assets rating
def rating_choice_handler(message):

    global search_improvement_list
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if message.text == "⭐":
        query_parameters["stars"] = 1

        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "⭐⭐":
        query_parameters["stars"] = 2
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "⭐⭐⭐":
        query_parameters["stars"] = 3
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "⭐⭐⭐⭐":
        query_parameters["stars"] = 4
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "⭐⭐⭐⭐⭐":
        query_parameters["stars"] = 5
        search_improvement_list.remove("Rating")
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "Want to add more preferences?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == "< Back":
        search_improvement_list = ["Accessibility", "Prices", "Rating"]
        create_keyboard(keyboard, search_improvement_list)
        keyboard.add(types.KeyboardButton("Show me results"))
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I can improve the search or show you the results. What can I do?",
                               reply_markup=keyboard)
        bot.send_message(message.chat.id, generate_search_improvement_choices(query_parameters))
        bot.register_next_step_handler(msg, search_improvements_handler)
    else:
        create_keyboard(keyboard, ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        keyboard.add(types.KeyboardButton("< Back"))

        msg = bot.send_message(message.chat.id, "I don't think I understand, could you choose from the options below?",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)


# FINAL STEP: show query result
def show_results_handler(message):

    global query_parameters
    query_string = query_KB(query_parameters)

    subdir = re.sub("eureka.*", "eureka", os.getcwd())
    os.chdir(subdir)
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog_thread:
            prolog_thread.query("consult(\"project/kb_configuration/KB.pl\")")

            global main_query_results
            main_query_results = prolog_thread.query(query_string)
            print(main_query_results)

            #if no results are found or if it's T/F query
            if type(main_query_results) == bool:
                if main_query_results:
                    bot.send_message(message.chat.id, "{}".format(main_query_results)) #TODO: evaluate if the bot need to do something when the result is True
                else:
                    bot.send_message(message.chat.id, "I did not find any results matching your search. /start again.", reply_markup=types.ReplyKeyboardRemove())
            else: #main_query_results is a list of dictonaries
                bot.send_message(message.chat.id, "Here it is some nice results: ", reply_markup=types.ReplyKeyboardRemove())
                if len(main_query_results) > 1:
                    keyboard = types.InlineKeyboardMarkup()
                    keyboard.add(types.InlineKeyboardButton(">", callback_data='item_1'))
                    caption = "*{}*. It was reviewed by users with {} star(s).".format(main_query_results[0]["Label"], main_query_results[0]["Star"])
                    if main_query_results[0]["TripID"] != "nan":
                        caption += " Check also what users say on [Tripadvisor](https://tripadvisor.com/{})!".format(str(main_query_results[0]["TripID"]))

                    if main_query_results[0]["Image"] == "nan":
                        bot.send_photo(message.chat.id, photo=IMAGE_PLACEHOLDER, caption=caption, reply_markup=keyboard, parse_mode='Markdown')
                    else:
                        bot.send_photo(message.chat.id, photo=main_query_results[0]["Image"], reply_markup=keyboard, caption=caption, parse_mode='Markdown')
                else:
                    caption = "*{}*. It was reviewed by users with {} star(s).".format(main_query_results[0]["Label"], main_query_results[0]["Star"])
                    if main_query_results[0]["TripID"] != "nan":
                        caption += " Check also what users say on [Tripadvisor](https://tripadvisor.com/{})!".format(str(main_query_results[0]["TripID"]))
                    if main_query_results[0]["Image"] == "nan":
                         bot.send_photo(message.chat.id, photo=IMAGE_PLACEHOLDER, caption=caption, parse_mode='Markdown')
                    else:
                        image = main_query_results[0]["Image"]
                        bot.send_photo(message.chat.id, photo=image, caption=caption, parse_mode='Markdown')
                bot.send_message(message.chat.id, "Press \"/start\" to go on with Pisa exploration!")

@bot.callback_query_handler(func=lambda call: 'item_' in call.data)
def carousel(call):
    index = int(call.data[4:].split('_')[1])
    keyboard = types.InlineKeyboardMarkup()

    caption = "*{}*. It was reviewed by users with {} star(s).".format(main_query_results[index]["Label"], main_query_results[index]["Star"])
    if main_query_results[index]["TripID"] != "nan":
        caption += " Check also what users say on [Tripadvisor](https://tripadvisor.com/{})!".format(str(main_query_results[index]["TripID"]))

    if index == 0:
        keyboard.add(types.InlineKeyboardButton('>', callback_data='item_1'))
    elif index == len(main_query_results) - 1:
        keyboard.add(types.InlineKeyboardButton('<', callback_data='item_{}'.format(str(index - 1))))
    else:
        keyboard.add(types.InlineKeyboardButton('<', callback_data='item_{}'.format(str(index - 1))), types.InlineKeyboardButton('>', callback_data='item_{}'.format(str(index + 1))))
    
    if main_query_results[index]["Image"] == "nan":
        bot.edit_message_media(media=types.InputMediaPhoto(IMAGE_PLACEHOLDER), chat_id=call.message.chat.id, message_id=call.message.id)
        bot.edit_message_caption(caption=caption, chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard, parse_mode='Markdown')
    else:
        image = main_query_results[index]["Image"]
        bot.edit_message_media(media=types.InputMediaPhoto(image), chat_id=call.message.chat.id, message_id=call.message.id)
        bot.edit_message_caption(caption=caption, chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard, parse_mode='Markdown')


bot.infinity_polling()
