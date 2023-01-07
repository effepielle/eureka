# TODO: register all callbacks

import emoji
import telebot
import bot_config as config

def _convert_to_attribute(text: str) -> str:
    return emoji.replace_emoji(text, "") \
            .strip() \
            .replace(" ", "_") \
            .replace("&", "AND") \
            .upper()


def _create_keyboard(keyboard, labels):
    button_list = []
    counter = 0
    for i in labels:
        button_list.append(telebot.types.KeyboardButton(i))
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

@config.bot_entity.message_handler(commands=['start'])
def main_category_choice_handler(message):
    config.bot_entity.send_message(message.chat.id,
            f"Hello {message.chat.first_name}! "
            f"I'm {config.BOT_NAME} and I can help you discover cultural assets in Pisa.")

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))
    #TODO: define some prolog rule like
    # artAndCulture(Id,....,Star) :- categoriesInArtAndCulture(Id,...,Star).
    #TODO: add also show result directly after the choice so that the
    # user can have different kind of tipology
    msg = config.bot_entity.send_message(message.chat.id,
            config.MESSAGE_CONSTANTS.CHOOSE_CATEGORY,
            reply_markup=keyboard
    )
    config.bot_entity.register_next_step_handler(msg, sub_category_choice_handler)


def sub_category_choice_handler(message):
    text = _convert_to_attribute(message.text)
    try:
        subcategory = config.SUBCATEGORIES[text]
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        _create_keyboard(keyboard, [dn for (dn, l) in vars(subcategory).values()])
        keyboard.add(telebot.types.KeyboardButton(config.MESSAGE_CONSTANTS.BACK))
        msg = config.bot_entity.send_message(message.chat.id, "Great!", reply_markup=keyboard)
        config.bot_entity.register_next_step_handler(msg, advanced_search_filter_handler)
    except KeyError:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))

        msg = config.bot_entity.send_message(message.chat.id,
                config.MESSAGE_CONSTANTS.CANNOT_UNDERSTAND,
                reply_markup=keyboard
        )
        config.bot_entity.register_next_step_handler(msg, main_category_choice_handler)


def advanced_search_filter_handler(message):
    return