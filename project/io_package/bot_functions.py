from types import SimpleNamespace

import emoji
import telebot
import bot_config as config

def _convert_to_attribute(text: str) -> str:
    return emoji.replace_emoji(text, "") \
            .strip() \
            .replace(" ", "_") \
            .replace("&", "AND") \
            .upper()

def _stringify_star_rating(rating: config.StarRating) -> str:
    value = rating.value
    if value is None:
        return "at least 0."
    else:
        return f"at least {str(value)}."

def _stringify_accessibility(accessibility: config.Accessibility) -> str:
    value = accessibility.value
    if value is None:
        return "no filters have been applied."
    else:
        return "wheelchair friendly."

def _stringify_prices(prices: config.Prices) -> str:
    value = prices.value
    if value is None:
        return "no filters have been applied."
    else:
        return f"at most {str(value)} euro(s)."

def _reset_query_filters(query_builder: SimpleNamespace) -> None:
    query_builder.ADDITIONAL_FILTERS.ACCESSIBILITY = config.Accessibility("♿ Accessibility")
    query_builder.ADDITIONAL_FILTERS.STAR_RATING = config.StarRating("⭐ Rating")
    query_builder.ADDITIONAL_FILTERS.PRICES = config.Prices("💶 Prices")
    return


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
    msg = config.bot_entity.send_message(message.chat.id,
            config.MESSAGE_CONSTANTS.CHOOSE_CATEGORY,
            reply_markup=keyboard
    )
    config.bot_entity.register_next_step_handler(msg, sub_category_choice_handler)


def sub_category_choice_handler(message):
    subcategory = None
    if config.QUERY_BUILDER.CATEGORY is None or message.text != config.MESSAGE_CONSTANTS.BACK:
        try:
            text = _convert_to_attribute(message.text)
            subcategory = config.SUBCATEGORIES[text]
            config.QUERY_BUILDER.CATEGORY = text
        except KeyError:
            keyboard = telebot.types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
            )
            _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))
            msg = config.bot_entity.send_message(message.chat.id,
                config.MESSAGE_CONSTANTS.CANNOT_UNDERSTAND,
                reply_markup=keyboard
            )
            config.bot_entity.register_next_step_handler(msg, main_category_choice_handler)
            return
    else:
        subcategory = config.SUBCATEGORIES[config.QUERY_BUILDER.CATEGORY]
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    _create_keyboard(keyboard, [dn for (dn, _) in vars(subcategory).values()])
    keyboard.add(telebot.types.KeyboardButton(config.MESSAGE_CONSTANTS.BACK))
    msg = config.bot_entity.send_message(message.chat.id, "Great!", reply_markup=keyboard)
    config.bot_entity.register_next_step_handler(msg, advanced_search_filter_handler)


def advanced_search_filter_handler(message):
    if message.text == config.MESSAGE_CONSTANTS.BACK and config.QUERY_BUILDER.SITE_TYPE is None:
        keyboard = telebot.types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
        )
        _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))
        msg = config.bot_entity.send_message(message.chat.id,
            config.MESSAGE_CONSTANTS.CHOOSE_CATEGORY,
            reply_markup=keyboard
        )
        _reset_query_filters(config.QUERY_BUILDER)
        config.bot_entity.register_next_step_handler(msg, main_category_choice_handler)
    else:
        if config.QUERY_BUILDER.SITE_TYPE is None:
            subcategory = config.SUBCATEGORIES[config.QUERY_BUILDER.CATEGORY]
            try:
                site_type = subcategory.__getattribute__(_convert_to_attribute(message.text))
                config.QUERY_BUILDER.SITE_TYPE = site_type.label
            except AttributeError:
                keyboard = telebot.types.ReplyKeyboardMarkup(
                            resize_keyboard=True,
                            one_time_keyboard=True
                )
                _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))
                msg = config.bot_entity.send_message(message.chat.id,
                    config.MESSAGE_CONSTANTS.CANNOT_UNDERSTAND,
                    reply_markup=keyboard
                )
                config.bot_entity.register_next_step_handler(msg, main_category_choice_handler)
        else:
            msg = (
                "I may either improve the search "
                "or show you the results. The following filters "
                "are available.\n"
                "**Accessibility**: "
                f"{_stringify_accessibility(config.QUERY_BUILDER.ADDITIONAL_FILTERS.ACCESSIBILITY)}"
                "\n**Star rating**: "
                f"{_stringify_star_rating(config.QUERY_BUILDER.ADDITIONAL_FILTERS.STAR_RATING)}"
                "\n**Price**:"
                f"{_stringify_prices(config.QUERY_BUILDER.ADDITIONAL_FILTERS.PRICES)}\n"
            )
            keyboard = telebot.types.ReplyKeyboardMarkup(
                        resize_keyboard=True,
                        one_time_keyboard=True
            )
            _create_keyboard(
                keyboard,
                [dn for (dn, _) in vars(config.QUERY_BUILDER.ADDITIONAL_FILTERS).values()]
            )
            keyboard.add(telebot.types.KeyboardButton(config.MESSAGE_CONSTANTS.SHOW_RESULTS))
            keyboard.add(telebot.types.KeyboardButton(config.MESSAGE_CONSTANTS.BACK))
            msg = config.bot_entity.send_message(message.chat.id, msg, reply_markup=keyboard)
            config.bot_entity.register_next_step(msg, additional_filter_handler)

def additional_filter_handler(message):
    if message.text == config.MESSAGE_CONSTANTS.BACK:
        keyboard = telebot.types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
        )
        _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))
        msg = config.bot_entity.send_message(message.chat.id,
            config.MESSAGE_CONSTANTS.CHOOSE_CATEGORY,
            reply_markup=keyboard
        )
        config.bot_entity.register_next_step_handler(msg, sub_category_choice_handler)
        _reset_query_filters(config.QUERY_BUILDER)
    elif message.text == config.MESSAGE_CONSTANTS.SHOW_RESULTS:
        config.bot_entity.register_next_step_handler(message, show_results_handler)
    else:
        text = _convert_to_attribute(message.text)
        try:
            additional_filter = config.QUERY_BUILDER.__getattribute__(text)
            keyboard = telebot.types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
            )
            if additional_filter == config.QUERY_BUILDER.ADDITIONAL_FILTERS.ACCESSIBILITY:
                msg = "Would you like to filter and see only wheelchair friendly sites?"
                _create_keyboard(keyboard, ["Yes", "No"])
                keyboard.add(telebot.types.KeyboardButton(config.MESSAGE_CONSTANTS.BACK))
                msg = config.bot_entity.send_message(message.chat.id, msg, reply_markup=keyboard)
                config.bot_entity.register_next_step(msg, accessibility_handler)
            elif additional_filter == config.QUERY_BUILDER.ADDITIONAL_FILTERS.STAR_RATING:
                msg = (
                    "Set a threshold value. "
                    "No sites the rating of which is lower than "
                    "this value shall be displayed."
                )
                _create_keyboard(keyboard, [i * "⭐" for i in range(1, 6)])
                keyboard.add(telebot.types.KeyboardButton(config.MESSAGE_CONSTANTS.BACK))
                msg = config.bot_entity.send_message(message.chat.id, msg, reply_markup=keyboard)
                config.bot_entity.register_next_step(msg, star_rating_handler)
            elif additional_filter == config.QUERY_BUILDER.ADDITIONAL_FILTERS.PRICES:
                msg = (
                    "Set a threshold value. "
                    "No sites the tickets' price of which is higher than "
                    "this value shall be displayed."
                )
                # TODO: create appropriate keyboard, register bot next step
            else:
                keyboard = telebot.types.ReplyKeyboardMarkup(
                            resize_keyboard=True,
                            one_time_keyboard=True
                )
                _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))
                msg = config.bot_entity.send_message(message.chat.id,
                    config.MESSAGE_CONSTANTS.CANNOT_UNDERSTAND,
                    reply_markup=keyboard
                )
                config.bot_entity.register_next_step_handler(msg, main_category_choice_handler)
        except AttributeError:
            keyboard = telebot.types.ReplyKeyboardMarkup(
                            resize_keyboard=True,
                            one_time_keyboard=True
            )
            _create_keyboard(keyboard, list(vars(config.CATEGORIES_LABELS).values()))
            msg = config.bot_entity.send_message(message.chat.id,
                config.MESSAGE_CONSTANTS.CANNOT_UNDERSTAND,
                reply_markup=keyboard
            )
            config.bot_entity.register_next_step_handler(msg, sub_category_choice_handler)

# TODO: implement these functions

def show_results_handler(message):
    if message.text == config.MESSAGE_CONSTANTS.BACK:
        config.bot_entity.register_next_step_handler(message, advanced_search_filter_handler)
        return

def accessibility_handler(message):
    if message.text == config.MESSAGE_CONSTANTS.BACK:
        config.bot_entity.register_next_step_handler(message, advanced_search_filter_handler)
        return

def star_rating_handler(message):
    if message.text == config.MESSAGE_CONSTANTS.BACK:
        config.bot_entity.register_next_step_handler(message, advanced_search_filter_handler)
        return