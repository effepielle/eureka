import os
import re

#change needed because of ide compatibility issues
def custom_abs_path(file):
    #simply truncate everything beyond eureka directory
    subdir = re.sub("eureka.*","eureka/project/config-files",os.getcwd())
    os.chdir(subdir)
    return os.path.abspath(file)

#### DIALOGFLOW ###

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = custom_abs_path("eureka-wlon-fb3248e88a69.json")
DIALOGFLOW_PROJECT_ID = 'eureka-wlon'
DIALOGFLOW_LANGUAGE_CODE = 'en'

#### DIALOGFLOW ###
TELEGRAM_TOKEN = '5689759624:AAHfrWL9xPd8KlG11ah1wm95EMago4TK6AI'


