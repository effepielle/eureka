import io
import re
from math import ceil
import pandas as pd
import os
import urllib
from PIL import Image
from telebot import types
from project.config_files.config import RESIZING_SIZE


def create_keyboard(keyboard, labels):
    """Create a Telegram keyboard using a labels list as buttons labels

    Args:
        keyboard: a generic Telegram keyboard object
        labels: a list of labels to be used as buttons labels
    """

    button_list = []
    counter = 0
    for i in labels:
        button_list.append(types.KeyboardButton(i))
        counter += 1
        if counter == 3:
            keyboard.row(button_list[0], button_list[1], button_list[2])
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


def convert_to_label(user_choice):
    """Convert a button label into the asset label used in the knowledge base 
        (eg. if user presses ⛪ Churches button, the function returns church_building used to identify churches in the knowledge base)

    Args:
        user_choice (str): label associated to the button pressed by the user

    Returns:
        str: corresponding label used in the knowledge base
    """
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
    """Create a message to summarize the user choices

    Args:
        my_dict: a dictionary containing the user choices

    Returns:
        str: the message to be sent to the user which summarizes the user choices 
    """

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
                string += "*Opening Days*:  Weekdays (Mon-Sat) \n"
            else:
                string += "*Opening Days*:  Sunday and Holidays \n"
        else:
            string += "*Opening Days*: All available days \n"

        if "hours" in my_dict["timetable_filter"]["fact"] and "selected_opening" in my_dict["timetable_filter"]:
            # doesn't matter if opening or closing, we control only if something change
            if my_dict["timetable_filter"]["selected_opening"] == "9.0":
                string += "*Opening Hours*:  9:00 - 12:00 \n"
            elif my_dict["timetable_filter"]["selected_opening"] == "13.0":
                string += "*Opening Hours*:  13:00 - 19:00 \n"
            else:
                string += "*Opening Hours*:  All available time to visit\n"

        else:
            string += "*Opening Hours*:  All available time to visit\n"

    else:
        string += "*Opening Days*:  All available days \n" \
            "*Opening Hours*:  All available time to visit\n"
    return string


def clean_filter(dict):
    """Remove the search improvement filters from the dictionary (if the user restart the search from scratch, the filters should be removed)

    Args:
        dict: dictionary containing the user selected search improvement choices
    """
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
    """Build the query string to be sent to the knowledge base

    Args:
        query_parameters: dictionary containing the user search preferences
        asset_type: type of asset to be searched in the knowledge base
        bad_weather: True if the weather is bad, False otherwise

    Returns:
        str: query string to be sent to the knowledge base through the swiplserver API
    """
    query_string = ""
    for key in query_parameters:

        if 'fact' in query_parameters[key] and query_parameters[key]['fact']:
            # dividing the fact (string or dict) from the rest of key, every predicate has same structure
            fact = query_parameters[key]['fact']
            query_parameters_copy = query_parameters[key].copy()
            del query_parameters_copy['fact']

            if key == "timetable_filter":
                if "days" in fact:
                    query_string += f"{fact['days']}(Day),"
                # reduce the dictionary into a string in both cases (with or without day fact)
                fact = fact['hours']

            query_string += f"{fact}("
            query_string += ", ".join(list(query_parameters_copy.values()))
            query_string += "),"

    query_string += f"is_type(Label,\"{asset_type}\")"

    # if it's raining we add the predicate to find indoor assets
    if bad_weather:
        query_string += ", visitable_if_raining(Label)"

    query_string += "."
    print(query_string)
    return query_string


def is_weather_bad():
    """Check if the weather is bad or not

    This is a dummy function, it always returns False and it's used to test the bot under certain weather conditions.
    For future development, it can be linked to an actual weather API or generate a random value.

    Returns:
        bool: a boolean value indicating if the wheather is bad or not
    """
    return False


def image_downloader(id, url):
    """Download the asset image from Wikidata and save it locally using the asset ID as name

    Args:
        id (str): asset unique identifier (Wikidata ID)
        url (str): image url

    Returns:
        str: local path of the image
    """
    subdir = re.sub("eureka.*", "eureka", os.getcwd())
    os.chdir(subdir)
    img_dir = os.path.join(subdir, "project/bot_backend/img")

    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    localPath = os.path.join(subdir, img_dir, "{}.jpg".format(id))

    if os.path.isfile(localPath) == False:

        urllib.request.urlretrieve(url, localPath)
        with open(localPath, 'rb+') as f:

            img = Image.open(io.BytesIO(f.read()))

            # create a thumbnail version of images whose shape doesn't exceed dim of thumbnail
            img.thumbnail((RESIZING_SIZE, RESIZING_SIZE))
            # Save the compressed image
            img.save(localPath, optimize=True, quality=80)

    return localPath


def clean_results(results_list):
    """Clean the results list from duplicates differentiating between the ones with and without days

    Args:
        results_list: list of dictionaries containing the results of the query to the knowledge base

    Returns:
        list: list of dictionaries containing the results of the query to the knowledge base without duplicates
    """
    # acts like preconditions to avoid errors
    if 'Day' in results_list[0]:
        cleaned_list = clean_results_with_days(results_list)
    else:
        cleaned_list = clean_results_no_days(results_list)
    return cleaned_list


def clean_results_no_days(results_list):
    """Clean the results list from duplicates in the case of no days in the query results

    Args:
        results_list: list of dictionaries containing the results of the query to the knowledge base

    Returns:
        list: list of dictionaries containing the results of the query to the knowledge base without duplicates
    """

    formatted_list = []
    for dicti in results_list:
        formatted_list.append(dicti)
        copy_list = results_list.copy()
        copy_list.remove(dicti)
        # eliminate from results_list - current element all the duplicates by label
        for dictj in copy_list:
            if dicti['Label'] == dictj['Label']:
                results_list.remove(dictj)
    return formatted_list


def clean_results_with_days(results_list):
    """Clean the results list from duplicates in the case of days in the query results

    Args:
        results_list: list of dictionaries containing the results of the query to the knowledge base 

    Returns:
        list: list of dictionaries containing the results of the query to the knowledge base without duplicates
    """

    formatted_query_results = []
    no_duplicate_list = []
    day_order = ["Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday"]

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
                            d['OpeningHours'].append(
                                str(dictj['Opening']) + ' - ' + str(dictj['Closing']))
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

    # to remove the duplicates in formatted_query_results
    for v in formatted_query_results:
        if v not in no_duplicate_list:
            no_duplicate_list.append(v)

    return no_duplicate_list
