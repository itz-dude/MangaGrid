# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

import concurrent.futures
import datetime
import json
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
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
            return 'webscrapping/chromedriver.exe'


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
            string[string.index('An')] = 1
        elif 'an' in string:
            string[string.index('an')] = 1

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
        with open(f"webscrapping/results/{archive}.json", "w") as mangas:  
            mangas.write(json.dumps(results, indent = 4))

        print(f'LOG: Results saved {archive}.json')



    # ------------------------------------------------- #
    # ------------------ BEHAVIORS -------------------- #
    # ------------------------------------------------- #

    def routine_initialization(self):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(self.manganato)
            task_2 = executor.submit(self.mangalife)

            task_1.result()
            task_2.result()

    # ------------------ MANGANATO -------------------- #

    def manganato(self):
        self.manganato_updates()


    def manganato_updates(self):
        self.browser(self.debug)
        self.driver.get('https://manganato.com/index.php')

        time.sleep(1)

        updates = {}

        try:
            div = self.waiting(self.driver, By.CLASS_NAME, 'content-homepage-item', plural=True)

            for item in div:
                image = self.waiting(item, By.CLASS_NAME, 'img-loading')
                title = self.waiting(item, By.CLASS_NAME, 'item-title')
                link = self.waiting(item, By.CLASS_NAME, 'a-h')
                chapter = self.waiting(item, By.CLASS_NAME, 'item-chapter')
                
                try:
                    author = self.waiting(item, By.CLASS_NAME, 'item-author')
                    author = author.text
                except NoSuchElementException:
                    author = None
                
                updated = self.get_timestamp_from_string(chapter.text.split('\n')[1])

                updates[title.text] = {
                    'link' : link.get_attribute('href'),
                    'author' : author,
                    'image' : image.get_attribute('src'),
                    'chapter' : chapter.text.split('\n')[0],
                    'updated' : f'{updated}',
                    'source' : 'Manganato'
                }

            self.dump_results('manganato_updates', updates)

            self.driver.quit()

        except Exception as e:
            print(f'LOG - ERROR: manganato_updates - {e}')
            self.driver.quit()

    def manganato_search(self, string):
        self.browser(self.debug)
        self.driver.get(f'https://manganato.com/search/story/{string.replace(" ", "_")}')

        time.sleep(1)

        search = {}

        try:
            div = self.waiting(self.driver, By.CLASS_NAME, 'search-story-item', plural=True)

            for item in div:
                image = self.waiting(item, By.CLASS_NAME, 'img-loading')
                title = self.waiting(item, By.CLASS_NAME, 'item-title')
                link = self.waiting(item, By.CLASS_NAME, 'item-title')
                chapter = self.waiting(item, By.CLASS_NAME, 'item-chapter')
                
                try:
                    author = self.waiting(item, By.CLASS_NAME, 'item-author')
                    author = author.text
                except NoSuchElementException:
                    author = None
                
                updated = self.waiting(item, By.CLASS_NAME, 'item-time')

                search[title.text] = {
                    'link' : link.get_attribute('href'),
                    'author' : author,
                    'image' : image.get_attribute('src'),
                    'chapter' : chapter.text,
                    'link_chapter' : chapter.get_attribute('href'),
                    'updated' : f'{updated.text[10:]}',
                    'source' : 'Manganato'
                }

            self.driver.quit()

            return search

        except Exception as e:
            print(f'LOG - ERROR: manganato_search - {e}')
            self.driver.quit()

            return {'error' : f'{e}'}


    # ------------------ MANGALIFE -------------------- #

    def mangalife(self):
        self.mangalife_updates()


    def mangalife_updates(self):
        self.browser(self.debug)
        self.driver.get('https://manga4life.com/')

        time.sleep(2)

        updates = {}

        try:
            latest_updates = self.waiting(self.driver, By.CLASS_NAME, 'LatestChapters')

            div = self.waiting(latest_updates, By.CLASS_NAME, 'Chapter', plural=True)

            for item in div:
                title = self.waiting(item, By.CLASS_NAME, 'SeriesName')
                image = self.waiting(item, By.CLASS_NAME, 'Image')
                link = self.waiting(image, By.TAG_NAME, 'a')
                image = self.waiting(image, By.TAG_NAME, 'img')
                chapter = self.waiting(item, By.CLASS_NAME, 'ChapterLabel')
                updated = self.waiting(item, By.CLASS_NAME, 'DateLabel')

                updated = self.get_timestamp_from_string(updated.text)

                updates[title.text] = {
                    'link' : link.get_attribute('href'),
                    'author' : 'none',
                    'image' : image.get_attribute('src'),
                    'chapter' : chapter.text,
                    'updated' : f'{updated}',
                    'source' : 'mangalife'
                }

            self.dump_results('mangalife_updates', updates)

            self.driver.quit()
        
        except Exception as e:
            print(f'LOG - ERROR: mangalife_updates - {e}')
            self.driver.quit()


    def mangalife_search(self, string):
        self.browser(self.debug)
        self.driver.get(f'https://manga4life.com/search/?name={string}')

        time.sleep(2)

        search = {}

        try:
            div = self.waiting(self.driver, By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[3]/div[1]/div')
            div = self.waiting(div, By.CLASS_NAME, 'top-15', plural=True)

            for index, item in enumerate(div):
                image = self.waiting(item, By.XPATH, f'/html/body/div[3]/div/div/div/div[2]/div[3]/div[1]/div/div[{index+1}]/div/div[1]/a/img')
                title = self.waiting(item, By.XPATH, f'/html/body/div[3]/div/div/div/div[2]/div[3]/div[1]/div/div[{index+1}]/div/div[2]/a')
                author = self.waiting(item, By.XPATH, f'/html/body/div[3]/div/div/div/div[2]/div[3]/div[1]/div/div[{index+1}]/div/div[2]/div[1]/span')
                chapter = self.waiting(item, By.XPATH, f'/html/body/div[3]/div/div/div/div[2]/div[3]/div[1]/div/div[{index+1}]/div/div[2]/div[3]/a')
                updated = self.waiting(item, By.CLASS_NAME, 'GrayLabel')

                search[title.text] = {
                    'image' : image.get_attribute('src'),
                    'link' : title.get_attribute('href'),
                    'author' : author.text,
                    'chapter' : chapter.text,
                    'link_chapter' : chapter.get_attribute('href'),
                    'updated' : f'{updated.text[1:]}',
                    'source' : 'Manganlife'
                }

            self.driver.quit()

            return search

        except Exception as e:
            print(f'LOG - ERROR: manganato_search - {e}')
            self.driver.quit()

            return {'error' : f'{e}'}


if __name__ == '__main__':
    MangaScrapping().routine_initialization()