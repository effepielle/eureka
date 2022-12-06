import os
import re
import sys
import telebot

import numpy as np
from swiplserver import PrologMQI


subdir = re.sub("eureka.*", "eureka", os.getcwd())
os.chdir(subdir)
sys.path.append('../eureka')

from project.config_files.config import TELEGRAM_TOKEN, IMAGE_PLACEHOLDER
from project.bot_backend.utilities import *


QUERY_PARAMETERS = {
    "fact": "",
    "ID": "Id",
    "label": "Label",
    "lat": "Lat",
    "lon": "Lon",
    "accessibility": "_",
    "tripadvisor_id": "TripID",
    "image": "Image",
    "stars": "Star"
}

# Contains the final query results.
# It needs to be here to be visible to callback query handler methods
MAIN_QUERY_RESULTS = None

BOT_NAME = "EUREKA"

# TODO: add more items
SITES_LIST = ["🏞️ Parks", "🌿 Public Gardens", "🧱 City Walls",
        "⛪ Churches", "🏙️ Squares", "🏛️ Museums", "🗽 Monuments"]  # "Cultural Events"

CANNOT_UNDERSTAND_MESSAGE = "I don't think I understand, could you choose from the options below?"
CHOOSE_A_CATEGORY_MESSAGE = "Let's start by choosing a category"
SHOW_ME_THE_RESULTS = "🔍 Show me the results"

ACCESSIBILITY = "♿ Accessibility"
STAR_RATING = "⭐ Rating"
PRICES = "💶 Prices"
BACK = "< Back"

ARTS_AND_CULTURE = "🏺 Arts & Culture"
ARCHITECTURE = "🏛️ Architecture"
GREEN_AREAS = "🌲 Green Areas"
CATEGORIES_LIST = [ARTS_AND_CULTURE, ARCHITECTURE, GREEN_AREAS]

SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES]
ORIGINAL_DIM_SEARCH_IMPROVEMENT = len(SEARCH_IMPROVEMENT_LIST)


# for testing: https://t.me/eurekachatbot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# STEP 0: bot is started and asks user to choose an asset category (Arts & Culture, Architecture, Green Areas)
@bot.message_handler(commands=['start'])
def handle_conversation(message):
    global SEARCH_IMPROVEMENT_LIST
    global QUERY_PARAMETERS

    bot.send_message(message.chat.id,
            f"Hello {message.chat.first_name}! "
            f"I'm {BOT_NAME} and I can help you discover cultural assets in Pisa.")

    SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES]
    QUERY_PARAMETERS = {
        "fact": "",
        "ID": "Id",
        "label": "Label",
        "lat": "Lat",
        "lon": "Lon",
        "accessibility": "_",
        "tripadvisor_id": "TripID",
        "image": "Image",
        "stars": "Star"
    }

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    create_keyboard(keyboard, CATEGORIES_LIST)
    #TODO: define some prolog rule like
    # artAndCulture(Id,....,Star) :- categoriesInArtAndCulture(Id,...,Star).
    #TODO: add also show result directly after the choice so that the
    # user can have different kind of tipology
    msg = bot.send_message(message.chat.id,
            CHOOSE_A_CATEGORY_MESSAGE,
            reply_markup=keyboard
    )
    bot.register_next_step_handler(msg, category_handler)


# STEP 0.1: bot asks user to select a sub-category (churches, monuments, towers, etc.)
def category_handler(message):
    great_msg = "Great!"
    if message.text == ARTS_AND_CULTURE:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        # TODO: fill the keyboard with remaining item
        create_keyboard(keyboard, ["🏛️ Museums"])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, great_msg, reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)
    elif message.text == ARCHITECTURE:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["🧱 City Walls", "⛪ Churches", "🏙️ Squares", "🗽 Monuments"])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, great_msg, reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)
    elif message.text == GREEN_AREAS:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, ["🏞️ Parks", "🌿 Public Gardens"])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, great_msg, reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)
    else:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, CATEGORIES_LIST)

        msg = bot.send_message(message.chat.id,
                CANNOT_UNDERSTAND_MESSAGE,
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, category_handler)


# STEP 1: the user choice is handled
def site_label_handler(message):
    # if the message is a sub-category (churches, monuments, towers, etc.)
    if message.text in SITES_LIST:
        # TODO
        QUERY_PARAMETERS["fact"] = convert_to_label(message.text)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, [ACCESSIBILITY, PRICES, STAR_RATING])
        # In this way you can separate Show results and back buttons from the rest of the group
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                "I can improve the search if you suggest other details "
                f"or show you the results for {message.text}",
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == BACK:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, CATEGORIES_LIST)

        msg = bot.send_message(message.chat.id,
                CHOOSE_A_CATEGORY_MESSAGE,
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, category_handler)

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, SITES_LIST)

        msg = bot.send_message(message.chat.id,
                CANNOT_UNDERSTAND_MESSAGE,
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, site_label_handler)


# STEP 2: check if user wants to add more details to the query (accessibility, cost, rating etc.). If not,
# the bot shows query results
def search_improvements_handler(message):
    global SEARCH_IMPROVEMENT_LIST

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    # if the message is a request for details
    if message.text == ACCESSIBILITY:
        create_keyboard(keyboard, ["Yes", "No"])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, "Are you in a wheelchair?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)

    # TODO
    elif message.text == PRICES:
        pass

    elif message.text == STAR_RATING:
        create_keyboard(keyboard, [i * "⭐" for i in range(1, 6)])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, "Choose the rating!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)


    elif message.text == SHOW_ME_THE_RESULTS:
        show_results_handler(message)

    elif message.text == BACK:

        if len(SEARCH_IMPROVEMENT_LIST) == ORIGINAL_DIM_SEARCH_IMPROVEMENT:
            create_keyboard(keyboard, CATEGORIES_LIST)
            # TODO keyboard.add(types.KeyboardButton(BACK))
            msg = bot.send_message(message.chat.id,
                    CHOOSE_A_CATEGORY_MESSAGE,
                    reply_markup=keyboard
            )
            bot.register_next_step_handler(msg, category_handler)

        else:
            SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, PRICES, STAR_RATING]
            create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
            keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
            keyboard.add(types.KeyboardButton(BACK))

            msg = bot.send_message(message.chat.id,
                    "I can improve the search or show you the results. What can I do?",
                    reply_markup=keyboard
            )
            bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS))
            bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        create_keyboard(keyboard, [ACCESSIBILITY, PRICES, STAR_RATING])
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


# STEP 2.1: checks whether the user is in a wheelchair
def accessibility_choice_handler(message):
    global SEARCH_IMPROVEMENT_LIST

    more_preferences_msg = "Want to add more preferences?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if message.text == "Yes":
        QUERY_PARAMETERS["accessibility"] = "wheelchair accessible"

        SEARCH_IMPROVEMENT_LIST.remove(ACCESSIBILITY)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                more_preferences_msg,
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "No":
        QUERY_PARAMETERS["accessibility"] = np.nan
        SEARCH_IMPROVEMENT_LIST.remove(ACCESSIBILITY)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                more_preferences_msg,
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == BACK:
        SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, PRICES, STAR_RATING]
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                "I can improve the search or show you the results. What can I do?",
                reply_markup=keyboard)
        bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS))
        bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        create_keyboard(keyboard, ["Yes", "No"])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)


# TODO
# STEP 2.2: checks user's price preferences about cultural assets
def prices_choice_handler(message):
    pass


# STEP 2.3: checks user's preferences about assets rating
def rating_choice_handler(message):
    global SEARCH_IMPROVEMENT_LIST
    global QUERY_PARAMETERS

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if "⭐" in message.text:
        QUERY_PARAMETERS["stars"] = message.text.count("⭐")
        SEARCH_IMPROVEMENT_LIST.remove(STAR_RATING)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                "Want to add more preferences?",
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, search_improvements_handler)
    elif message.text == BACK:
        SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, PRICES, STAR_RATING]
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                "I can improve the search or show you the results. What can I do?",
                reply_markup=keyboard
        )
        bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS))
        bot.register_next_step_handler(msg, search_improvements_handler)
    else:
        create_keyboard(keyboard, [i * "⭐" for i in range(1, 6)])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)


# FINAL STEP: show query result
def show_results_handler(message):
    global QUERY_PARAMETERS
    global MAIN_QUERY_RESULTS

    query_string = query_KB(QUERY_PARAMETERS)
    subdir = re.sub("eureka.*", "eureka", os.getcwd())
    os.chdir(subdir)

    could_not_find_matches_msg = ("I did not find any results matching your search, but don't worry, "
                            "just press /start again and continue to explore!"
    )
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog_thread:
            prolog_thread.query("consult(\"project/kb_configuration/KB.pl\")")

            MAIN_QUERY_RESULTS = prolog_thread.query(query_string)
            #if no results are found or if it's T/F query
            if isinstance(MAIN_QUERY_RESULTS, bool):
                if MAIN_QUERY_RESULTS:
                    # TODO: evaluate if the bot need to do something when the result is True
                    bot.send_message(message.chat.id, f"{MAIN_QUERY_RESULTS}")
                else:
                    bot.send_message(message.chat.id,
                            could_not_find_matches_msg,
                            reply_markup=types.ReplyKeyboardRemove()
                    )
            else: #MAIN_QUERY_RESULTS is a list of dictonaries
                if MAIN_QUERY_RESULTS:
                    bot.send_message(message.chat.id,
                            "Here are some nice results tailored for your preferences. "
                            "To make another search press /start again!",
                            reply_markup=types.ReplyKeyboardRemove()
                    )

                    if MAIN_QUERY_RESULTS[0]["Image"] == "nan":
                        image = image_downloader("PLACEHOLDER", IMAGE_PLACEHOLDER)
                    else:
                        image = image_downloader(MAIN_QUERY_RESULTS[0]["Id"],
                                MAIN_QUERY_RESULTS[0]["Image"]
                        )

                    #Prolog shows only dict of unified free vars, fixed value on Prolog query isn't
                    # shown todo with all possible fixable values of the query
                    # but in the script we excluded query with:
                    # TripID, Image, Lat, Lon instantiable and accessibility is set "_" by default
                    if "Star" in MAIN_QUERY_RESULTS[0]:
                        caption = (
                                f"*{MAIN_QUERY_RESULTS[0]['Label']}*. "
                                "It has been reviewed by users with "
                                f"{MAIN_QUERY_RESULTS[0]['Star']} star(s)."
                        )
                    else:
                        caption = (
                                f"*{MAIN_QUERY_RESULTS[0]['Label']}*. "
                                "It has been reviewed by users with "
                                f"{QUERY_PARAMETERS['stars']} star(s)."
                        )
                    if MAIN_QUERY_RESULTS[0]["TripID"] != "nan":
                        caption += (
                                " Check out what users say on "
                                "[Tripadvisor]"
                                f"(https://tripadvisor.com/{str(MAIN_QUERY_RESULTS[0]['TripID'])})!"
                        )
                    keyboard = types.InlineKeyboardMarkup()
                    keyboard.add(types.InlineKeyboardButton("📍 Get Location",
                            callback_data=(
                                    "coordinates_"
                                    f"{MAIN_QUERY_RESULTS[0]['Lat']}"
                                    f"_{MAIN_QUERY_RESULTS[0]['Lon']}"
                                    "_0")
                            )
                    )

                    if len(MAIN_QUERY_RESULTS) > 1:
                        keyboard.add(types.InlineKeyboardButton('Next', callback_data='item_1'))
                        bot.send_photo(message.chat.id,
                                photo=open(image, 'rb'),
                                reply_markup=keyboard,
                                caption=caption,
                                parse_mode='Markdown'
                        )
                    else:
                        bot.send_photo(message.chat.id,
                                photo=open(image, 'rb'),
                                reply_markup=keyboard,
                                caption=caption,
                                parse_mode='Markdown'
                        )
                else:
                    bot.send_message(message.chat.id,
                            could_not_find_matches_msg,
                            reply_markup=types.ReplyKeyboardRemove()
                    )

@bot.callback_query_handler(func=lambda call: 'item_' in call.data)
def carousel(call):
    index = int(call.data[4:].split('_')[1])
    keyboard = types.InlineKeyboardMarkup()

    if MAIN_QUERY_RESULTS[index]["Image"] == "nan":
        image = image_downloader("PLACEHOLDER", IMAGE_PLACEHOLDER)
    else:
        image = image_downloader(MAIN_QUERY_RESULTS[index]["Id"],
                        MAIN_QUERY_RESULTS[index]["Image"])

    caption = f"*{MAIN_QUERY_RESULTS[index]['Label']}*. "

    # Prolog shows only dict of unified free vars, fixed value on Prolog query isn't shown todo
    # with all possible fixable values of the query but in the script we excluded query with:
    # TripID, Image, Lat, Lon instantiable and accessibility is set "_" by default
    if "Star" in MAIN_QUERY_RESULTS[index]:
        caption += f" It has been reviewed by users with {MAIN_QUERY_RESULTS[index]['Star']} star(s)."
    else:
        caption = (
                f"*{MAIN_QUERY_RESULTS[index]['Label']}*. "
                f"It has been reviewed by users with {QUERY_PARAMETERS['stars']} star(s)."
        )

    if MAIN_QUERY_RESULTS[index]["TripID"] != "nan":
        caption += (
                " Check out what users say on [Tripadvisor]"
                f"(https://tripadvisor.com/{str(MAIN_QUERY_RESULTS[index]['TripID'])})!"
        )

    keyboard.add(
            types.InlineKeyboardButton("📍 Get Location", callback_data=(
                    f"coordinates_{MAIN_QUERY_RESULTS[index]['Lat']}"
                    f"_{MAIN_QUERY_RESULTS[index]['Lon']}"
                    f"_{str(index)}"
            ))
    )
    if index == 0:
        keyboard.add(types.InlineKeyboardButton('Next' , callback_data='item_1'))
    elif index == len(MAIN_QUERY_RESULTS) - 1:
        keyboard.add(types.InlineKeyboardButton('Prev.' , callback_data=f'item_{str(index - 1)}'))
    else:
        keyboard.add(types.InlineKeyboardButton('Prev.' , callback_data=f'item_{str(index - 1)}'),
                types.InlineKeyboardButton('Next', callback_data=f'item_{str(index + 1)}'))

    bot.edit_message_media(media=types.InputMediaPhoto(open(image, 'rb')),
            chat_id=call.message.chat.id, message_id=call.message.id)
    bot.edit_message_caption(caption=caption, chat_id=call.message.chat.id,
            message_id=call.message.id, reply_markup=keyboard, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: 'coordinates_' in call.data)
def send_asset_location(call):
    lat = call.data[11:].split('_')[1]
    lon = call.data[11:].split('_')[2]
    index = int(call.data[11:].split('_')[3])

    bot.send_message(call.message.chat.id,
            f"This is the location for *{MAIN_QUERY_RESULTS[index]['Label']}*.",
            parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    bot.send_location(call.message.chat.id, latitude=lat, longitude=lon)

#TODO: check wheater condition with the dedicated method and make a query for indoor/outdoor (e.g bad weather -> indoor) and show another carousel of results with a message like Since today it's rainy here it is some results...

bot.infinity_polling()
