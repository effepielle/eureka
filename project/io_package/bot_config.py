from collections import namedtuple
import os
import re
import sys
from types import SimpleNamespace
import telebot


BOT_NAME = "EUREKA"
IMAGE_PLACEHOLDER = (
    'https://cdn.dribbble.com/users/'
    '1004013/screenshots/16268886/media/'
    'f9564be2057af9d0abd61fecf2f6699a.jpg'
)

MESSAGE_CONSTANTS = SimpleNamespace()
MESSAGE_CONSTANTS.CANNOT_UNDERSTAND = (
    "I don't think I understand, "
    "could you choose from the options below?"
)
MESSAGE_CONSTANTS.CHOOSE_CATEGORY = "Let's start by choosing a category"
MESSAGE_CONSTANTS.SHOW_RESULTS = "🔍 Show me the results"

CATEGORIES_LABELS = SimpleNamespace()
CATEGORIES_LABELS.ARTS_AND_CULTURE = "🏺 Arts & Culture"
CATEGORIES_LABELS.ARCHITECTURE = "🏛️ Architecture"
CATEGORIES_LABELS.GREEN_AREAS = "🌲 Green Areas"

Accessibility = namedtuple(
    "Accessibility", [
        "display_name",
        "query_if_filter_is_toggled_on",
        "value"
    ],
    defaults=[None]
)

StarRating = namedtuple("StarRating", ["display_name", "value"], defaults=[None])
Prices = namedtuple(
    "Prices",
    ["display_name", "value"],
    defaults=[None]
)
QueryParameter = namedtuple("QueryParameter", ["label", "value"])
QUERY_BUILDER = SimpleNamespace()
QUERY_BUILDER.ADDITIONAL_FILTERS = SimpleNamespace()
QUERY_BUILDER.ADDITIONAL_FILTERS.ACCESSIBILITY = Accessibility("♿ Accessibility")
QUERY_BUILDER.ADDITIONAL_FILTERS.STAR_RATING = StarRating("⭐ Star Rating")
QUERY_BUILDER.ADDITIONAL_FILTERS.PRICES = Prices("💶 Prices")
QUERY_BUILDER.SITE_TYPE = None
Subcategory = namedtuple("Subcategory", ["display_name", "label"])

SUBCATEGORIES = dict()
SUBCATEGORIES["ARTS_AND_CULTURE"] = SimpleNamespace()
SUBCATEGORIES["ARTS_AND_CULTURE"].MUSEUMS = Subcategory("🏛️ Museums", "museum")
SUBCATEGORIES["ARTS_AND_CULTURE"].THEATRES = Subcategory("🎪 Theatres", "theatre")
SUBCATEGORIES["ARTS_AND_CULTURE"].ART_VENUES = Subcategory("🎨 Art venues", "art_venue")
SUBCATEGORIES["ARTS_AND_CULTURE"].LIBRARIES = Subcategory("📚 Libraries", "library")
SUBCATEGORIES["ARCHITECTURE"] = SimpleNamespace()
SUBCATEGORIES["ARCHITECTURE"].CHURCHES = Subcategory("⛪ Churches", "church_building")
SUBCATEGORIES["ARCHITECTURE"].PALACES = Subcategory("🏘️ Palaces", "palace")
SUBCATEGORIES["ARCHITECTURE"].CITY_WALLS = Subcategory("🧱 City Walls", "city_wall")
SUBCATEGORIES["ARCHITECTURE"].MONUMENTS = Subcategory("🗽 Monuments", "monument")
SUBCATEGORIES["ARCHITECTURE"].TOWERS = Subcategory("🗼 Towers", "tower")
SUBCATEGORIES["ARCHITECTURE"].BRIDGES = Subcategory("🌉 Bridges", "bridge")
SUBCATEGORIES["ARCHITECTURE"].CITY_GATES = Subcategory("🚪 City gates", "city_gate")
SUBCATEGORIES["ARCHITECTURE"].CEMETERIES = Subcategory("⚰️ Public cemeteries", "cemetery")
SUBCATEGORIES["ARCHITECTURE"].SQUARES = Subcategory("🏙️ Squares", "square")
SUBCATEGORIES["GREEN_AREAS"] = SimpleNamespace()
SUBCATEGORIES["GREEN_AREAS"].GARDENS = Subcategory("🌿 Public Gardens", "public_garden")
SUBCATEGORIES["GREEN_AREAS"].PARKS = Subcategory("🏞️ Parks", "park")


subdir = re.sub("eureka.*", "eureka", os.getcwd())
os.chdir(subdir)
sys.path.append('../eureka')

bot_entity = telebot.TeleBot('5689759624:AAHXdHxfT1-rTMGD-vQHeIaqYJ1dQrxoESU')
