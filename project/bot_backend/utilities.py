import io
import re
from math import ceil

import pandas as pd
from PIL import Image
from telebot import types
import random
import os
import platform
import urllib
from urllib import request

# Takes a Telegram Keyboard object and a list of labels and creates buttons, three for each keyboard's row
from telebot.apihelper import ApiTelegramException


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
    asset_dict = {
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
        "🎭 Theatres": "theater"
    }
    return asset_dict[user_choice]

def generate_search_improvement_choices(my_dict):
    string = f"*Current choices:* \n"
    dict_key = my_dict.keys()


    if "accessibility_filter" in dict_key and "fact" in my_dict["accessibility_filter"]:
        if my_dict["accessibility_filter"]["fact"] == "is_wheelchair_friendly":
            string += "*Accessibility*:  wheelchair friendly\n"
        else:
            string += "*Accessibility*:  wheelchair friendly & unfriendly\n"
    else:
        string += "*Accessibility*:  N/A\n"


    if "rating_filter" in dict_key and "fact" in my_dict["rating_filter"]:
        string += f"*Rating*:  {my_dict['rating_filter']['threshold']} star(s) \n"
    else:
        string += "*Rating*:  all ratings\n"


    if "cost_filter" in dict_key and "fact" in my_dict["cost_filter"]:
        if "free_entry" in my_dict["cost_filter"]["fact"]:
            string += "*Cost*:  Free entrance \n"
        elif "filter_by_cost" in my_dict["cost_filter"]["fact"]:
            if "lower_threshold" and "upper_threshold" in my_dict["cost_filter"]:
                string += f"*Cost*:  {my_dict['cost_filter']['lower_threshold']} € - {my_dict['cost_filter']['upper_threshold']} € \n"
            elif "threshold" in my_dict["cost_filter"]:
                string += f"*Cost*:  from {my_dict['cost_filter']['threshold']} € \n"
    else:
        string += "*Cost*:  all costs \n"


    if "timetable_filter" in dict_key and "fact" in my_dict["timetable_filter"]:
        if "days" in my_dict["timetable_filter"]["fact"]:
            if "weekday" in my_dict["timetable_filter"]["fact"]["days"]:
                string+="*Opening Days*:  Weekdays (Mon-Sat) \n"
            else:
                string+="*Opening Days*:  Sunday and Holidays \n"
        else:
            string+="*Opening Days*: All available days \n"

        if "hours" in my_dict["timetable_filter"]["fact"] and "selected_opening" in my_dict["timetable_filter"]:
                #doesn't matter if opening or closing, we control only if something change
                if my_dict["timetable_filter"]["selected_opening"] == "9.0":
                    string+="*Opening Hours*:  9:00 - 12:00 \n"
                elif my_dict["timetable_filter"]["selected_opening"] == "13.0":
                    string+="*Opening Hours*:  13:00 - 19:00 \n"
                else:
                    string += "*Opening Hours*:  All available time to visit\n"

        else:
            string += "*Opening Hours*:  All available time to visit\n"

    else:
        string+="*Opening Days*:  All available days \n" \
                "*Opening Hours*:  All available time to visit\n"
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


def query_KB(query_parameters, asset_type, bad_weather):
    query_string = ""
    for key in query_parameters:

        if 'fact' in query_parameters[key] and query_parameters[key]['fact']:
            #dividing the fact (string or dict) from the rest of key, every predicate has same structure
            fact = query_parameters[key]['fact']
            query_parameters_copy = query_parameters[key].copy()
            del query_parameters_copy['fact']

            # it only changes
            if key == "timetable_filter":
                if "days" in fact:
                    query_string += f"{fact['days']}(Day),"
                #we reduce the only dictionary fact into a single value fact
                fact = fact['hours']

            query_string += f"{fact}("
            query_string += ", ".join(list(query_parameters_copy.values()))
            query_string += "),"

    query_string += f"is_type(Label,\"{asset_type}\")"

    #if it's raining
    if bad_weather:
        query_string +=", visitable_if_raining(Label)"

    query_string += "."

    #print(query_string)

    return query_string

def is_wheather_bad():
    # fixed prior value, no bad weather
    return False
    # future development: e.g. random choice return random.choice([True, False])
    # or link an actual api for weather forecasting

#necessary since current standard by TelegramBotAPI 10 MB i.e. 10000000 bytes
RESIZING_SIZE=1024
def image_downloader(id, url):
    subdir = re.sub("eureka.*", "eureka", os.getcwd())
    os.chdir(subdir)
    img_dir = os.path.join(subdir, "project/bot_backend/img")

    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    localPath = os.path.join(subdir, img_dir, "{}.jpg".format(id))

    if os.path.isfile(localPath) == False:

        urllib.request.urlretrieve(url, localPath)
        #print(os.path.getsize(localPath))
        with open(localPath, 'rb+') as f:

            img = Image.open(io.BytesIO(f.read()))

            #create a thumbnail vers of images whose shape doesn't exceed dim of thumbnail
            img.thumbnail((RESIZING_SIZE, RESIZING_SIZE))
            # Save the compressed image
            img.save(localPath, optimize=True, quality=80)
        #if image too big
        #if os.path.getsize(localPath) > MAX_SIZE_SUPPORTED:
        #    os.remove(localPath)

    return localPath

def clean_results(results_list):
    #preconditions
    if 'Day' in results_list[0]:
        cleaned_list = clean_results_with_days(results_list)
    else:
        cleaned_list = clean_results_no_days(results_list)
    return cleaned_list

def clean_results_no_days(results_list):

    formatted_list = []
    for dicti in results_list:
        formatted_list.append(dicti)
        copy_list = results_list.copy()
        copy_list.remove(dicti)
        #eliminate from results_list - current element all the duplicates by label
        for dictj in copy_list:
            if dicti['Label'] == dictj['Label']:
                results_list.remove(dictj)

    #if still some kind duplicates (not needed)
    #for v in formatted_list:
    #    if v not in no_duplicate_list:
    #        no_duplicate_list.append(v)
    #return no_duplicate_list

    return formatted_list

def clean_results_with_days(results_list):

    formatted_query_results = []
    no_duplicate_list = []
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for dicti in results_list:

        dicti_copy = dicti.copy()
        del dicti_copy['Day']
        del dicti_copy['Opening']
        del dicti_copy['Closing']

        dicti_copy['OpeningDays'] = []

        for dictj in results_list:

            if dictj['Label'] == dicti_copy['Label']:
                dictj['Day'] = dictj['Day'].capitalize()
                is_present = False
                for d in dicti_copy['OpeningDays']:
                    if dictj['Day'] == d['Day']:
                        is_present = True
                        # check if opening hours are already present
                        if str(dictj['Opening']) + ' - ' + str(dictj['Closing']) not in d['OpeningHours']:
                            d['OpeningHours'].append(str(dictj['Opening']) + ' - ' + str(dictj['Closing']))
                        break
                if not is_present:
                    dicti_copy['OpeningDays'].append(
                        {
                            'Day': dictj['Day'],
                            'OpeningHours': [str(dictj['Opening']) + ' - ' + str(dictj['Closing'])]
                        }
                    )

        dicti_copy['OpeningDays'].sort(key=lambda k: day_order.index(k['Day']))
        formatted_query_results.append(dicti_copy)

    # to remove the duplicates in resulting list
    for v in formatted_query_results:
        if v not in no_duplicate_list:
            no_duplicate_list.append(v)

    return no_duplicate_list


