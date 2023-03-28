import re

import pandas as pd
from telebot import types
import random
import os
import platform
import urllib
from urllib import request

# Takes a Telegram Keyboard object and a list of labels and creates buttons, three for each keyboard's row
def create_keyboard(keyboard, labels):
    button_list = []
    counter = 0
    for i in labels:
        button_list.append(types.KeyboardButton(i))
        counter += 1
        if counter == 3:
            keyboard.row(button_list[0],button_list[1],button_list[2])
            button_list = []
            counter = 0
        elif labels.index(i) == len(labels)-1:
            if counter == 2:
                keyboard.row(button_list[0], button_list[1])
                button_list = []
                counter = 0
            elif counter == 1:
                keyboard.row(button_list[0])
                button_list = []
                counter = 0
    # keyboard.add(types.KeyboardButton("Parks"), types.KeyboardButton("Public Garden"), types.KeyboardButton("City Walls"))
    # keyboard.add(types.KeyboardButton("Churches"))

#convert user choice in the form of KB label (e.g. if users choices Churches the function should return church_building)
def convert_to_label(user_choice): 
    dict = {
        "⛪ Churches": "church_building",
        "🏞️ Parks": "park", 
        "🌿 Public Gardens": "public_garden", 
        "🧱 City Walls": "city_walls",
        "🏙️ Squares": "square", 
        "🏛️ Museums": "museum",
        "🗽 Monuments": "monument",
        "🏘️ Palaces": "palace",
        "🗼 Towers": "tower",
        "🌉 Bridges": "bridge",
        "🚪 City gates": "city_gate",
        "⚰️ Public cemeteries": "cemetery",
        "📚 Libraries": "library",
        "🎨 Art venues": "arts_venue",
        "🎪 Theatres": "theater"
        #TODO: reset when user pushes back
    }
    return dict[user_choice]

def generate_search_improvement_choices(dict):
    string = "Current choices: \n"
    dict_key = dict.keys()


    if "accessibility_filter" in dict_key and "fact" in dict["accessibility_filter"]:
        if dict["accessibility_filter"]["fact"] == "is_wheelchair_friendly":
            string += "Accessibility: wheelchair friendly\n"
        else:
            string += "Accessibility: wheelchair friendly & unfriendly\n"
    else:
        string += "Accessibility: N/A\n"


    if "rating_filter" in dict_key and "fact" in dict["rating_filter"]:
        string += f"Rating: {dict['rating_filter']['threshold']} star(s) \n"
    else:
        string += "Rating: all ratings\n"


    if "cost_filter" in dict_key and "fact" in dict["cost_filter"]:
        if "free_entry" in dict["cost_filter"]["fact"]:
            string += "Cost: Free entrance \n"
        elif "filter_by_cost" in dict ["cost_filter"]["fact"]:
            if "lower_threshold" and "upper_threshold" in dict["cost_filter"]:
                string += f"Cost: {dict['cost_filter']['lower_threshold']} € - {dict['cost_filter']['upper_threshold']} € \n"
            elif "threshold" in dict["cost_filter"]:
                string += f"Cost: from {dict['cost_filter']['threshold']} € \n"
    else:
        string += "Cost: all costs \n"

    #TODO
    #if "timetable_filter" in dict_key and "fact" in dict["timetable_filter"]:
    #    "Timetable: Mon-Sat, orario..."

    return string

def clean_filter(dict):
    dict_key = dict.keys()
    if "accessibility_filter" in dict_key and "fact" in dict["accessibility_filter"]:
        del dict["accessibility_filter"]
    if "rating_filter" in dict_key and "fact" in dict["rating_filter"]:
        del dict["rating_filter"]

    if "cost_filter" in dict_key and "fact" in dict["cost_filter"]:
        del dict["cost_filter"]

    if "timetable_filter" in dict_key and "fact" in dict["timetable_filter"]:
        del dict["timetable_filter"]


def query_KB(query_parameters):
    query_string = ""
    for key in query_parameters:
        if key == "fact":
            query_string += "{}(".format(query_parameters[key])
        elif key == "accessibility" and pd.notna(query_parameters[key]) and query_parameters[key] != "_":
            query_string += "\"{}\",".format(query_parameters[key])
        elif key:
            query_string += "{},".format(query_parameters[key])

    # TODO: to update if we add different way of searching facts
    query_string += ")."
    query_string = re.sub(",+\)\.", ").", query_string)
    return query_string

def is_wheather_bad():
    return random.choice([True, False])

def image_downloader(id, url):
    subdir = re.sub("eureka.*", "eureka", os.getcwd())
    os.chdir(subdir)
    img_dir = os.path.join(subdir, "project/bot_backend/img")

    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    localPath = os.path.join(subdir, img_dir, "{}.jpg".format(id))


    if os.path.isfile(localPath) == False:
        urllib.request.urlretrieve(url, localPath)

    return localPath




