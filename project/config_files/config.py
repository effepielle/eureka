import os

#### DIALOGFLOW ###
DIALOGFLOW_PROJECT_ID = 'eureka-wlon'
DIALOGFLOW_LANGUAGE_CODE = 'en'

#change needed because cd is in "...\project\io-package" and there is no .json in it
def costum_abs_path(file):
    os.chdir("..\config_files")
    return os.path.abspath(file)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = costum_abs_path("eureka-wlon-fb3248e88a69.json")
TELEGRAM_TOKEN = '5689759624:AAHfrWL9xPd8KlG11ah1wm95EMago4TK6AI'

