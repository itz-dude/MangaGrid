# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

import datetime
import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class MangaScrapping():

    def __init__(self):
        self.debug = False    

    @property
    def driver_path(self):
        if sys.platform == 'linux':
            return '/usr/bin/geckodriver'
        elif sys.platform == 'win32':
            return 'manga/chromedriver.exe'


    # ------------------------------------------------- #
    # -------------------- TOOLS ---------------------- #
    # ------------------------------------------------- #

    def waiting(self, driver, tag = By.XPATH, tag_name = '', plural = False):
        if plural:
            return WebDriverWait(driver, 20).until(ec.presence_of_all_elements_located((tag, tag_name)))
        else:
            return WebDriverWait(driver, 20).until(ec.presence_of_element_located((tag, tag_name)))


    def browser(self, showing = False):
        if sys.platform == 'linux':
            c = DesiredCapabilities.FIREFOX
            c["pageLoadStrategy"] = "none"
            self.driver = webdriver.Firefox(service=Service(self.driver_path), desired_capabilities=c)

        elif sys.platform == 'win32':
            c = DesiredCapabilities.CHROME
            options = Options()
            if not showing:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(service=Service(self.driver_path), desired_capabilities=c, options=options)
            self.driver.minimize_window()


    def get_timestamp_from_string(self, string):
        dicti = {
            'sec' : ['seconds', 'second', 'secs'],
            'min' : ['minutes', 'minute', 'mins'],
            'hour' : ['hours'],
            'day' : ['days'],
            'week' : ['weeks'],
            'month' : ['months'],
            'year' : ['years']
        }
    
        for key in dicti.keys():    
            for value in dicti[key]:
                string = string.replace(value, key)

        string = string.split(' ')
        if 'in' in string:
            string.remove('in')

        if 'An' in string:
            string[string.index('An')] = '1'
        elif 'an' in string:
            string[string.index('an')] = '1'

        if 'sec' in ' '.join(string):
            return datetime.datetime.now() - datetime.timedelta(seconds=int(string[0]))
        elif 'min' in ' '.join(string):
            return datetime.datetime.now() - datetime.timedelta(minutes=int(string[0]))
        elif 'hour' in ' '.join(string):
            return datetime.datetime.now() - datetime.timedelta(hours=int(string[0]))
        elif 'day' in ' '.join(string):
            return datetime.datetime.now() - datetime.timedelta(days=int(string[0]))
        elif 'month' in ' '.join(string):
            return datetime.datetime.now() - datetime.timedelta(days=int(string[0]) * 30)
        elif 'year' in ' '.join(string):
            return datetime.datetime.now() - datetime.timedelta(days=int(string[0]) * 365)
        else:
            print(f'Error: Invalid date format - {string}')
            return datetime.datetime.now()


    def get_date_from_string(self, string):
        return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')


    def get_string_from_timestamp(self, timestamp):
        """
        This function will receive a time stamp and the output will be:
        'X secs ago', 'X hours ago' or 'X days ago'.
        """
        now = datetime.datetime.now()
        delta = now - timestamp
        if delta.days > 0:
            return f'{delta.days} days ago'
        elif delta.seconds > 0 and delta.seconds < 60:
            return f'{delta.seconds} secs ago'
        elif delta.seconds > 60 and delta.seconds < 3600:
            return f'{delta.seconds // 60} mins ago'
        elif delta.seconds > 3600 and delta.seconds < 86400:
            return f'{delta.seconds // 3600} hours ago'
        elif delta.seconds > 86400 and delta.seconds < 604800:
            return f'{delta.seconds // 86400} days ago'
        elif delta.seconds > 604800 and delta.seconds < 31536000:
            return f'{delta.seconds // 604800} weeks ago'
        elif delta.seconds > 31536000:
            return f'{delta.seconds // 31536000} years ago'


    def dump_results(self, archive, results):
        with open(f"manga/results/{archive}.json", "w") as mangas:  
            mangas.write(json.dumps(results, indent = 4))

        print(f'LOG: Results saved {archive}.json')

    def sanitize_string(self, source, string):
        dic = {
            'manganato' : {
                "_" : [" ", "'", ",", "-"],
                "" : ["?", "!", '"', "."],
            },
            'mangahere' : {
                "_" : [" ", "-"],
                "" : [":", "!", "?", ";", ",", "."],
            }
        }

        for key in dic[source].keys():
            for value in dic[source][key]:
                string = string.replace(value, key)

        return string


if __name__ == '__main__':
    pass