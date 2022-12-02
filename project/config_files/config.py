import os
import re
#### DIALOGFLOW ###
DIALOGFLOW_PROJECT_ID = 'eureka-wlon'
DIALOGFLOW_LANGUAGE_CODE = 'en'

#change needed because of ide compatibility issues
def custom_abs_path(file):
    #simply truncate everything beyond eureka directory
    subdir = re.sub("eureka.*","eureka/project/config_files",os.getcwd())
    os.chdir(subdir)
    return os.path.abspath(file)

#TODO: check how to make it works on Windows (path of credentials)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = custom_abs_path("eureka-wlon-fb3248e88a69.json")
TELEGRAM_TOKEN = '5689759624:AAHfrWL9xPd8KlG11ah1wm95EMago4TK6AI'

