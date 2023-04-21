import os
import re

# change needed because of ide compatibility issues


def custom_abs_path(file):
    # simply truncate everything beyond eureka directory
    subdir = re.sub("eureka.*", "eureka/project/config_files", os.getcwd())
    os.chdir(subdir)
    return os.path.abspath(file)


TELEGRAM_TOKEN = '5689759624:AAHXdHxfT1-rTMGD-vQHeIaqYJ1dQrxoESU'

# the chatbot uses this placeholder when an asset doesn't have an image (change the url to your own favorite placeholder image)
IMAGE_PLACEHOLDER = 'https://cdn.dribbble.com/users/1004013/screenshots/16268886/media/f9564be2057af9d0abd61fecf2f6699a.jpg'

# image resizing size limit since Telegram Bot API only allows 10 MB images i.e. 10000000 bytes
RESIZING_SIZE = 1024
