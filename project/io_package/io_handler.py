import os
import re
import sys

import telebot
from swiplserver import PrologMQI

subdir = re.sub("eureka.*", "eureka", os.getcwd())
os.chdir(subdir)
sys.path.append('../eureka')

from project.config_files.config import TELEGRAM_TOKEN, IMAGE_PLACEHOLDER
from project.bot_backend.utilities import *

# clean the filters of KB query
QUERY_PARAMETERS = {
    "recommendation":
        {"fact": "",
         "label": "Label",
         "lat": "Lat",
         "lon": "Lon",
         "rating": "Rating",
         "image": "Image",
         "trip_id": "TripID",
         "cost": "Cost"
}
}

# Contains the final query results.
# It needs to be here to be visible to callback query handler methods
MAIN_QUERY_RESULTS = None

BOT_NAME = "EUREKA"

'''
SITES_LIST = ["🏞️ Parks", "🌿 Public Gardens", "🧱 City Walls",
        "⛪ Churches", "🏙️ Squares", "🏛️ Museums",
        "🏘️ Palaces", "🗽 Monuments", "🗼 Towers",
        "🌉 Bridges", "🚪 City gates", "⚰️Public cemeteries",
              "📚 Libraries", "🎨 Art venues", "🎭 Theatres" ]
'''

CANNOT_UNDERSTAND_MESSAGE = "I don't think I understand, could you choose from the options below?"
CHOOSE_A_CATEGORY_MESSAGE = "Let's start by choosing a category"
SHOW_ME_THE_RESULTS = "🔍 Show me the results"

# user choice
ACCESSIBILITY = "♿ Accessibility"
STAR_RATING = "⭐ Rating"
PRICES = "💶 Prices" #FREE_ENTRY = "🆓 Free entry"
HOURS = "🕒 Opening Hours"
DAYS = "📅 Opening Days"

#TODO based on wheater condition

BACK = "< Back"

ARTS_AND_CULTURE = "🏺 Arts & Culture"
ARCHITECTURE = "🏛️ Architecture"
GREEN_AREAS = "🌲 Green Areas"

CATEGORIES_LIST = [ARTS_AND_CULTURE, ARCHITECTURE, GREEN_AREAS]
SELECTED_CATEGORY = None
SELECTED_ASSET_TYPE = None

SUBCATEGORIES_DICT = {
    "Arts_and_culture":["🏛️ Museums","🎭 Theatres","🎨 Art venues","📚 Libraries"],
    "Architecture":["⛪ Churches","🏘️ Palaces","🧱 City Walls",
                    "🗽 Monuments","🗼 Towers","🌉 Bridges","🚪 City gates",
                    "⚰️ Public cemeteries","🏙️ Squares"],
    "Green_areas":["🌿 Public Gardens", "🏞️ Parks"]
}

SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]
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

    SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]

    #clean the filters of KB query, because at the end of first successful interaction, we can digit /start and do another interaction,
    # but QUERY_PARAMETERS will be the same if not cleaned
    QUERY_PARAMETERS = {
        "recommendation":
            {   "fact": "",
                "label": "Label",
                "lat": "Lat",
                "lon": "Lon",
                "rating": "Rating",
                "image": "Image",
                "trip_id": "TripID",
                "cost": "Cost"
                }
    }

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    create_keyboard(keyboard, CATEGORIES_LIST)

    msg = bot.send_message(message.chat.id,
            CHOOSE_A_CATEGORY_MESSAGE,
            reply_markup=keyboard
    )
    bot.register_next_step_handler(msg, category_handler)


# STEP 0.1: bot manage the user selection of a sub-category (churches, monuments, towers, etc.)
def category_handler(message):
    global SELECTED_CATEGORY
    great_msg = "Great!"

    if message.text == ARTS_AND_CULTURE:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, SUBCATEGORIES_DICT["Arts_and_culture"])
        keyboard.add(types.KeyboardButton(BACK))
        SELECTED_CATEGORY = "Arts_and_culture"

        msg = bot.send_message(message.chat.id, great_msg, reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)

    elif message.text == ARCHITECTURE:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, SUBCATEGORIES_DICT["Architecture"])
        keyboard.add(types.KeyboardButton(BACK))
        SELECTED_CATEGORY = "Architecture"

        msg = bot.send_message(message.chat.id, great_msg, reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)

    elif message.text == GREEN_AREAS:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, SUBCATEGORIES_DICT["Green_areas"])
        keyboard.add(types.KeyboardButton(BACK))
        SELECTED_CATEGORY = "Green_areas"

        msg = bot.send_message(message.chat.id, great_msg, reply_markup=keyboard)
        bot.register_next_step_handler(msg, site_label_handler)

    #there is no back in this case, so it's only user typing something incorrect
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, CATEGORIES_LIST)

        msg = bot.send_message(message.chat.id,
                CANNOT_UNDERSTAND_MESSAGE,
                reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, category_handler)

        #if you want, optionally clean SELECTED_CATEGORY


# STEP 1: the user choice is handled
def site_label_handler(message):
    global SELECTED_ASSET_TYPE
    # if the message is a sub-category (churches, monuments, towers, etc.)
    if message.text in SUBCATEGORIES_DICT[SELECTED_CATEGORY]:
        SELECTED_ASSET_TYPE = message.text
        QUERY_PARAMETERS["recommendation"]["fact"] = "recommended_cultural_asset"

        #go to addictional filter
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS])
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

    #robust to error, it returns to the same methods
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        create_keyboard(keyboard, SUBCATEGORIES_DICT[SELECTED_CATEGORY])
        keyboard.add(types.KeyboardButton(BACK))

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


    elif message.text == PRICES:
        create_keyboard(keyboard, ["FREE ENTRY", "1.00 € - 5.00 €", "FROM 5.00 €"])
        keyboard.add(types.KeyboardButton(BACK))
        msg = bot.send_message(message.chat.id, "Choose your desired price range!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, prices_choice_handler)

    elif message.text == STAR_RATING:
        create_keyboard(keyboard, [i * "⭐" for i in range(1, 6)])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, "Choose a minimum rating!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)


    elif message.text == DAYS:

        create_keyboard(keyboard, ["Weekdays (Mon-Sat)", "Sunday and Holidays"])
        keyboard.add(types.KeyboardButton(BACK))
        msg = bot.send_message(message.chat.id, "Choose your desired days!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, timetable_day_choice_handler)

    elif message.text == HOURS:

        create_keyboard(keyboard, ["9:00 - 12:00", "13:00 - 19:00"])
        keyboard.add(types.KeyboardButton(BACK))
        msg = bot.send_message(message.chat.id, "Choose your time for your visit!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, timetable_hours_choice_handler)

    #TODO update everything
    elif message.text == SHOW_ME_THE_RESULTS:
        show_results_handler(message)

    elif message.text == BACK:

        if len(SEARCH_IMPROVEMENT_LIST) == ORIGINAL_DIM_SEARCH_IMPROVEMENT:
            create_keyboard(keyboard, CATEGORIES_LIST)

            msg = bot.send_message(message.chat.id,
                    CHOOSE_A_CATEGORY_MESSAGE,
                    reply_markup=keyboard
            )

            clean_filter(QUERY_PARAMETERS)
            bot.register_next_step_handler(msg, category_handler)

        else:
            SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]
            create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
            keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
            keyboard.add(types.KeyboardButton(BACK))

            msg = bot.send_message(message.chat.id,
                    "I can improve the search or show you the results. What can I do?",
                    reply_markup=keyboard
            )
            bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS),  parse_mode="markdown")
            bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        create_keyboard(keyboard, [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS])
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, search_improvements_handler)


# STEP 2.1: checks whether the user is in a wheelchair
def accessibility_choice_handler(message):
    global SEARCH_IMPROVEMENT_LIST
    global QUERY_PARAMETERS

    #next step message
    more_preferences_msg = "Want to add more preferences?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if "accessibility_filter" not in QUERY_PARAMETERS:
        QUERY_PARAMETERS["accessibility_filter"] = dict()
        QUERY_PARAMETERS["accessibility_filter"]["label"] = QUERY_PARAMETERS["recommendation"]["label"]


    if message.text == "Yes":
        QUERY_PARAMETERS["accessibility_filter"]["fact"]= "is_wheelchair_friendly"

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
        QUERY_PARAMETERS["accessibility_filter"]["fact"] = "is_wheelchair_unfriendly"

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

        #need to roll back the updates
        SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                "I can improve the search or show you the results. What can I do?",
                reply_markup=keyboard)
        bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS), parse_mode="markdown")
        bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        create_keyboard(keyboard, ["Yes", "No"])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, accessibility_choice_handler)


# STEP 2.2: checks user's price preferences about cultural assets
def prices_choice_handler(message):
    global SEARCH_IMPROVEMENT_LIST
    global QUERY_PARAMETERS

    # next step message
    more_preferences_msg = "Want to add more preferences?"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if "cost_filter" not in QUERY_PARAMETERS:
        QUERY_PARAMETERS["cost_filter"] = dict()
        QUERY_PARAMETERS["cost_filter"]["label"] = QUERY_PARAMETERS["recommendation"]["label"]
        QUERY_PARAMETERS["cost_filter"]["cost"] = QUERY_PARAMETERS["recommendation"]["cost"]


    if message.text == "FREE ENTRY":
        QUERY_PARAMETERS["cost_filter"]["fact"] = "free_entry"

        SEARCH_IMPROVEMENT_LIST.remove(PRICES)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               more_preferences_msg,
                               reply_markup=keyboard
                               )
        bot.register_next_step_handler(msg, search_improvements_handler)


    #taken only integer (not decimal like 0.50) to simplify query handling
    elif message.text == "1.00 € - 5.00 €":

        QUERY_PARAMETERS["cost_filter"]["fact"] = "filter_by_cost"
        QUERY_PARAMETERS["cost_filter"]["lower_threshold"] = "1.0"
        QUERY_PARAMETERS["cost_filter"]["upper_threshold"] = "5.0"

        SEARCH_IMPROVEMENT_LIST.remove(PRICES)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               more_preferences_msg,
                               reply_markup=keyboard
                               )
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == "FROM 5.00 €":

        QUERY_PARAMETERS["cost_filter"]["fact"] = "filter_by_cost"
        QUERY_PARAMETERS["cost_filter"]["threshold"] = "5.0"

        SEARCH_IMPROVEMENT_LIST.remove(PRICES)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               more_preferences_msg,
                               reply_markup=keyboard
                               )
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == BACK:

        # need to roll back the updates
        SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               "I can improve the search or show you the results. What can I do?",
                               reply_markup=keyboard)
        bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS),  parse_mode="markdown")
        bot.register_next_step_handler(msg, search_improvements_handler)


    else:
        create_keyboard(keyboard, ["FREE ENTRY", "1.00 € - 5.00 €", "FROM 5.00 €"])
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, prices_choice_handler)

# STEP 2.3: checks user's preferences about assets rating
def rating_choice_handler(message):
    global SEARCH_IMPROVEMENT_LIST
    global QUERY_PARAMETERS

    if "rating_filter" not in QUERY_PARAMETERS:
        QUERY_PARAMETERS["rating_filter"] = dict()
        QUERY_PARAMETERS["rating_filter"]["label"] = QUERY_PARAMETERS["recommendation"]["label"]
        QUERY_PARAMETERS["rating_filter"]["rating"] = QUERY_PARAMETERS["recommendation"]["rating"]


    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if "⭐" in message.text:

        QUERY_PARAMETERS["rating_filter"]["fact"] = "filter_by_star"
        QUERY_PARAMETERS["rating_filter"]["threshold"] = f"{message.text.count('⭐')}"

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
        SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                "I can improve the search or show you the results. What can I do?",
                reply_markup=keyboard
        )
        bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS),  parse_mode="markdown")
        bot.register_next_step_handler(msg, search_improvements_handler)
    else:
        create_keyboard(keyboard, [i * "⭐" for i in range(1, 6)])
        keyboard.add(types.KeyboardButton(BACK))
        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, rating_choice_handler)

# STEP 2.4: checks user's day preferences about cultural assets
def timetable_day_choice_handler(message):
    global SEARCH_IMPROVEMENT_LIST
    global QUERY_PARAMETERS

    if "timetable_filter" not in QUERY_PARAMETERS:
        QUERY_PARAMETERS["timetable_filter"] = dict()
        QUERY_PARAMETERS["timetable_filter"]["label"] = QUERY_PARAMETERS["recommendation"]["label"]
        QUERY_PARAMETERS["timetable_filter"]["fact"]=dict()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if "Weekdays (Mon-Sat)" in message.text:
        QUERY_PARAMETERS["timetable_filter"]["fact"]["days"] = "weekday"
        QUERY_PARAMETERS["timetable_filter"]["day"] = "Day"

        # if a range of hours not already selected
        if "hours" not in QUERY_PARAMETERS["timetable_filter"]["fact"]:
            QUERY_PARAMETERS["timetable_filter"]["fact"]["hours"] = "site_timetable"
            QUERY_PARAMETERS["timetable_filter"]["opening"] = "Opening"
            QUERY_PARAMETERS["timetable_filter"]["closing"] = "Closing"

        SEARCH_IMPROVEMENT_LIST.remove(DAYS)

        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               "Want to add more preferences?",
                               reply_markup=keyboard
                               )
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif "Sunday and Holidays" in message.text:
        QUERY_PARAMETERS["timetable_filter"]["fact"]["days"] = "holiday"
        QUERY_PARAMETERS["timetable_filter"]["day"] = "Day"

        # if a range of hours not already selected
        if "hours" not in QUERY_PARAMETERS["timetable_filter"]["fact"]:
            QUERY_PARAMETERS["timetable_filter"]["fact"]["hours"] = "site_timetable"
            QUERY_PARAMETERS["timetable_filter"]["opening"] = "Opening"
            QUERY_PARAMETERS["timetable_filter"]["closing"] = "Closing"

        SEARCH_IMPROVEMENT_LIST.remove(DAYS)

        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               "Want to add more preferences?",
                               reply_markup=keyboard
                               )
        bot.register_next_step_handler(msg, search_improvements_handler)


    elif message.text == BACK:

        SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               "I can improve the search or show you the results. What can I do?",
                               reply_markup=keyboard
                               )

        bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS),  parse_mode="markdown")
        bot.register_next_step_handler(msg, search_improvements_handler)

    else:
        create_keyboard(keyboard, ["Weekdays (Mon-Sat)", "Sunday and Holidays"])
        keyboard.add(types.KeyboardButton(BACK))
        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, timetable_day_choice_handler)

#STEP 2.5: checks user's hours preferences about cultural assets
def timetable_hours_choice_handler(message):
    global SEARCH_IMPROVEMENT_LIST
    global QUERY_PARAMETERS

    if "timetable_filter" not in QUERY_PARAMETERS:
        QUERY_PARAMETERS["timetable_filter"] = dict()
        QUERY_PARAMETERS["timetable_filter"]["label"] = QUERY_PARAMETERS["recommendation"]["label"]
        QUERY_PARAMETERS["timetable_filter"]["fact"]=dict()



    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if "9:00 - 12:00" in message.text:
        QUERY_PARAMETERS["timetable_filter"]["fact"]["hours"] = "filter_by_timetable"
        QUERY_PARAMETERS["timetable_filter"]["day"] = "Day"
        QUERY_PARAMETERS["timetable_filter"]["opening"] = "Opening"
        QUERY_PARAMETERS["timetable_filter"]["closing"] = "Closing"
        QUERY_PARAMETERS["timetable_filter"]["selected_opening"] = "9.0"
        QUERY_PARAMETERS["timetable_filter"]["selected_closing"] = "12.0"

        SEARCH_IMPROVEMENT_LIST.remove(HOURS)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               "Want to add more preferences?",
                               reply_markup=keyboard
                               )
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif "13:00 - 19:00" in message.text:
        QUERY_PARAMETERS["timetable_filter"]["fact"]["hours"] = "filter_by_timetable"
        QUERY_PARAMETERS["timetable_filter"]["day"] = "Day"
        QUERY_PARAMETERS["timetable_filter"]["opening"] = "Opening"
        QUERY_PARAMETERS["timetable_filter"]["closing"] = "Closing"
        QUERY_PARAMETERS["timetable_filter"]["selected_opening"] = "13.0"
        QUERY_PARAMETERS["timetable_filter"]["selected_closing"] = "19.0"


        SEARCH_IMPROVEMENT_LIST.remove(HOURS)
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               "Want to add more preferences?",
                               reply_markup=keyboard
                               )
        bot.register_next_step_handler(msg, search_improvements_handler)

    elif message.text == BACK:

        SEARCH_IMPROVEMENT_LIST = [ACCESSIBILITY, STAR_RATING, PRICES, DAYS, HOURS]
        create_keyboard(keyboard, SEARCH_IMPROVEMENT_LIST)
        keyboard.add(types.KeyboardButton(SHOW_ME_THE_RESULTS))
        keyboard.add(types.KeyboardButton(BACK))

        msg = bot.send_message(message.chat.id,
                               "I can improve the search or show you the results. What can I do?",
                               reply_markup=keyboard
                               )
        bot.send_message(message.chat.id, generate_search_improvement_choices(QUERY_PARAMETERS),  parse_mode="markdown")
        bot.register_next_step_handler(msg, search_improvements_handler)
    else:
        create_keyboard(keyboard, ["9:00 - 12:00", "13:00 - 19:00"])
        keyboard.add(types.KeyboardButton(BACK))
        msg = bot.send_message(message.chat.id, CANNOT_UNDERSTAND_MESSAGE, reply_markup=keyboard)
        bot.register_next_step_handler(msg, timetable_hours_choice_handler)




# FINAL STEP: show query result
def show_results_handler(message):
    global QUERY_PARAMETERS
    global MAIN_QUERY_RESULTS

    bad_weather = is_wheather_bad()
    asset_type = convert_to_label(SELECTED_ASSET_TYPE)
    query_string = query_KB(QUERY_PARAMETERS, asset_type, bad_weather)
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
                    bot.send_message(message.chat.id, f"{MAIN_QUERY_RESULTS}")
                else:
                    bot.send_message(message.chat.id,
                            could_not_find_matches_msg,
                            reply_markup=types.ReplyKeyboardRemove()
                    )
            # MAIN_QUERY_RESULTS is a list of dictonaries
            else:

                if MAIN_QUERY_RESULTS:

                    #remove duplicate and formatting from results
                    MAIN_QUERY_RESULTS = clean_results(MAIN_QUERY_RESULTS)

                    weather_message = ""
                    if bad_weather:
                        weather_message = "\nSince it will rain, I already filter for you some nice indoor places to visit 😇.\n"


                    bot.send_message(message.chat.id,
                            f"Here are some nice results tailored for your preferences. {weather_message}"
                            "To make another search press /start again!",
                            reply_markup=types.ReplyKeyboardRemove()
                    )

                    if MAIN_QUERY_RESULTS[0]["Image"] == "":
                        image = image_downloader("PLACEHOLDER", IMAGE_PLACEHOLDER)
                    else:
                        image = image_downloader(MAIN_QUERY_RESULTS[0]["Label"],
                                MAIN_QUERY_RESULTS[0]["Image"]
                        )
                        # if image too big, will not be loaded
                        if os.path.isfile(image) == False:
                            image = image_downloader("PLACEHOLDER", IMAGE_PLACEHOLDER)

                    #Prolog shows only dict of unified free vars, fixed value on Prolog query isn't
                    # shown todo with all possible fixable values of the query

                    if "Rating" in MAIN_QUERY_RESULTS[0]:
                        caption = (
                                f"*{MAIN_QUERY_RESULTS[0]['Label']}*. "
                                "\n\nIt has been reviewed by users with "
                                f"{MAIN_QUERY_RESULTS[0]['Rating']} star(s).\n"
                        )

                    if MAIN_QUERY_RESULTS[0]["Cost"] != -1.0:
                        if MAIN_QUERY_RESULTS[0]["Cost"] == 0.0:
                            caption += (
                                f"The entrance is free!\n"
                            )
                        else:
                            caption += (
                                    f"The ticket cost is "
                                    f"{MAIN_QUERY_RESULTS[0]['Cost']} €.\n"
                            )

                    if 'OpeningDays' in MAIN_QUERY_RESULTS[0]:

                        full_caption = ""
                        for dicti in MAIN_QUERY_RESULTS[0]['OpeningDays']:

                            hours_caption = ""
                            for hour in dicti['OpeningHours']:
                                hours_caption += hour.replace(".",":").replace(":0",":00").replace(":3",":30")
                                hours_caption += " "
                            full_caption += f"*{dicti['Day']}* :  {hours_caption}\n"

                        caption += (
                            f"The opening days with the corresponding opening hours are the followings:\n"
                            f"{full_caption}\n"
                        )

                    if MAIN_QUERY_RESULTS[0]["TripID"] != "":
                        caption += (
                                "Check out what users say on "
                                "[Tripadvisor]"
                                f"(https://tripadvisor.com/{str(MAIN_QUERY_RESULTS[0]['TripID'])})!"
                        )
                    keyboard = types.InlineKeyboardMarkup()

                    #TODO aggiungere controllo altrimenti stampa + volte la location
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

    if MAIN_QUERY_RESULTS[index]["Image"] == "":
        image = image_downloader("PLACEHOLDER", IMAGE_PLACEHOLDER)
    else:

        image = image_downloader(MAIN_QUERY_RESULTS[index]["Label"],
                                 MAIN_QUERY_RESULTS[index]["Image"]
                                 )
        #if image too big, will not be loaded
        if os.path.isfile(image) == False:
            image = image_downloader("PLACEHOLDER", IMAGE_PLACEHOLDER)

    # Prolog shows only dict of unified free vars, fixed value on Prolog query isn't
    # shown todo with all possible fixable values of the query

    if "Rating" in MAIN_QUERY_RESULTS[index]:
        caption = (
            f"*{MAIN_QUERY_RESULTS[index]['Label']}*. "
            "\n\nIt has been reviewed by users with "
            f"{MAIN_QUERY_RESULTS[index]['Rating']} star(s).\n"
        )

    if MAIN_QUERY_RESULTS[index]["Cost"] != -1.0:
        if MAIN_QUERY_RESULTS[0]["Cost"] == 0.0:
            caption += (
                f"The entrance is free!\n"
            )
        else:
            caption += (
                f"The ticket cost is "
                f"{MAIN_QUERY_RESULTS[index]['Cost']} €.\n"
            )

    if 'OpeningDays' in MAIN_QUERY_RESULTS[index]:

        full_caption = ""
        for dicti in MAIN_QUERY_RESULTS[index]['OpeningDays']:

            hours_caption = ""
            for hour in dicti['OpeningHours']:
                hours_caption += hour.replace(".", ":").replace(":0",":00").replace(":3",":30")
                hours_caption += " "
            full_caption += f"*{dicti['Day']}* :  {hours_caption} "

        caption += (
            f"The opening days with the corresponding opening hours are the followings:\n"
            f"{full_caption}\n"
        )

    if MAIN_QUERY_RESULTS[index]["TripID"] != "":
        caption += (
            "Check out what users say on "
            "[Tripadvisor]"
            f"(https://tripadvisor.com/{str(MAIN_QUERY_RESULTS[index]['TripID'])})!"
        )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📍 Get Location",
                                            callback_data=(
                                                "coordinates_"
                                                f"{MAIN_QUERY_RESULTS[index]['Lat']}"
                                                f"_{MAIN_QUERY_RESULTS[index]['Lon']}"
                                                f"_{str(index)}")
                                            )
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

bot.infinity_polling()
