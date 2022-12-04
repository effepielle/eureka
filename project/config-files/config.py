import os
import re

#change needed because of ide compatibility issues
def custom_abs_path(file):
    #simply truncate everything beyond eureka directory
    subdir = re.sub("eureka.*","eureka/project/config-files",os.getcwd())
    os.chdir(subdir)
    return os.path.abspath(file)

TELEGRAM_TOKEN = '5689759624:AAHfrWL9xPd8KlG11ah1wm95EMago4TK6AI'


