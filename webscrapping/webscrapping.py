# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

import concurrent.futures
import datetime
import json
import requests
import sys
import time
import threading

from bs4 import BeautifulSoup

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
        self.auto_update = True
        self.auto_update_interval = 180

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
        with open(f"webscrapping/results/{archive}.json", "w") as mangas:  
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

    # ------------------------------------------------- #
    # ------------------ BEHAVIORS -------------------- #
    # ------------------------------------------------- #

    def routine_initialization(self):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(self.manganato)
            task_2 = executor.submit(self.mangalife)
            task_3 = executor.submit(self.mangahere)

            task_1.result()
            task_2.result()
            task_3.result()

    # ------------------ MANGANATO -------------------- #

    def manganato(self):
        self.manganato_updates()


    def manganato_updates(self):
        file = requests.get("https://manganato.com/index.php")
        doc = BeautifulSoup(file.text, 'html.parser')

        updates = {}

        latest_updates = doc.find_all('div', class_='panel-content-homepage')[0]
        div = latest_updates.find_all('div', class_='content-homepage-item')

        for item in div:
            manga_link = item.find('a')
            image = manga_link.find('img')
            title = item.find('h3', class_='item-title')
            author = item.find('span', class_='item-author')

            ext = item.find('p', class_='item-chapter')
            chapter = ext.find('a')
            updated = ext.find('i')
            
            updates[title.text.replace('\n', '')] = {
                'link' : f'/manga_viewer?source=manganato&id={manga_link["href"].split("/")[-1]}',
                'author' : author.text.replace('\n', '') if author else '',
                'image' : image['src'],
                'chapter' : chapter.text.replace('\n', ''),
                'chapter_link' : chapter['href'],
                'updated' : f'{self.get_timestamp_from_string(updated.text)}',
                'source' : 'manganato',
                'ref' : manga_link['href'].split('/')[-1]
            }

        self.dump_results('manganato_updates', updates)


    def manganato_search(self, string):
        string = self.sanitize_string('manganato', string)
        
        file = requests.get(f'https://manganato.com/search/story/{string}')
        doc = BeautifulSoup(file.text, 'html.parser')

        search = {}

        result = doc.find('div', class_='panel-search-story')
        div = result.find_all('div', class_='search-story-item')

        for item in div:
            manga_link = item.find('a')
            image = manga_link.find('img')
            title = item.find('a', class_='item-title')
            author = item.find('span', class_='item-author')

            chapter = item.find('a', class_='item-chapter')
            updated = item.find('span', class_="item-time")
            
            search[title.text.replace('\n', '')] = {
                'link' : f'/manga_viewer?source=manganato&id={manga_link["href"].split("/")[-1]}',
                'author' : author.text.replace('\n', ''),
                'image' : image['src'],
                'chapter' : chapter.text.replace('\n', ''),
                'chapter_link' : chapter['href'],
                'updated' : updated.text.replace('\n', '')[10:],
                'source' : 'manganato',
                'ref' : manga_link['href'].split('/')[-1]
            }

        return search

    
    def manganato_access_manga(self, ref):
        file = requests.get(f'https://readmanganato.com/{ref}')
        doc = BeautifulSoup(file.text, 'html.parser')

        test_404 = doc.find('div', class_='panel-not-found')
        if test_404:
            return None

        manga = {}

        panel = doc.find('div', class_='panel-story-info')
        image = panel.find('div', class_='story-info-left').find('img')['src']

        panel_right = panel.find('div', class_='story-info-right')
        title = panel_right.find('h1').text

        subpanel = panel_right.find('table', class_='variations-tableInfo')
        ext = subpanel.find_all('tr')

        try:
            author = ext[1].find('td', class_='table-value').find_all('a')
            author = [a.text for a in author]
        except:
            author = []

        status = ext[2].find('td', class_='table-value').text

        try:
            genres = ext[3].find('td', class_='table-value').find_all('a')
            genres = [g.text for g in genres]
        except:
            genres = []

        ext = panel_right.find('div', class_='story-info-right-extent').find_all('p')

        updated = ext[0].find('span', class_='stre-value').text
        views = ext[1].find('span', class_='stre-value').text

        description = panel.find('div', class_='panel-story-info-description').text.replace('\nDescription :\n', '')


        manga_list = doc.find('div', class_='panel-story-chapter-list')
        chapters = manga_list.find('ul', class_='row-content-chapter').find_all('li')

        chapters_list = []
        for chapter in chapters:
            c_link = chapter.find('a')
            c_updt = chapter.find('span', class_='chapter-time')

            chapters_list.append({
                'title' : c_link.text,
                'chapter_link' : c_link['href'],
                'updated' : c_updt.text.replace('\n', '')
            })

            
        return {
            'title' : title.replace('\n', ''),
            'image' : image,
            'author' : author,
            'status' : status,
            'genres' : genres,
            'updated' : updated,
            'views' : views,
            'description' : description.replace('<br>', ' '),
            'chapters' : chapters_list,
            'source' : 'manganato'
        }


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

            for index, item in enumerate(div):
                title = self.waiting(item, By.CLASS_NAME, 'SeriesName')
                image = self.waiting(item, By.CLASS_NAME, 'Image')
                link = self.waiting(image, By.TAG_NAME, 'a')
                image = self.waiting(image, By.TAG_NAME, 'img')
                chapter = self.waiting(item, By.CLASS_NAME, 'ChapterLabel')
                chapter_link = self.waiting(item, By.XPATH, f'/html/body/div[3]/div/div[5]/div/div[2]/div[1]/div[{index+1}]/span/div/div[2]/a')
                updated = self.waiting(item, By.CLASS_NAME, 'DateLabel')

                updated = self.get_timestamp_from_string(updated.text)

                updates[title.text] = {
                    'link' : link.get_attribute('href'),
                    'author' : 'none',
                    'image' : image.get_attribute('src'),
                    'chapter' : chapter.text,
                    'chapter_link' : chapter_link.get_attribute('href'),
                    'updated' : f'{updated}',
                    'source' : 'mangalife',
                    'ref' : link.get_attribute('href').split('/')[-1]
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
                    'source' : 'manganlife',
                    'ref' : title.get_attribute('href').split('/')[-1]
                }

            self.driver.quit()

            return search

        except Exception as e:
            print(f'LOG - ERROR: manganato_search - {e}')
            self.driver.quit()

            return {'error' : f'{e}'}



    # ------------------ MANGAHERE -------------------- #

    def mangahere(self):
        self.mangahere_updates()


    def mangahere_updates(self):
        file = requests.get("https://www.mangahere.cc/latest/")
        doc = BeautifulSoup(file.text, 'html.parser')

        updates = {}

        latest_updates = doc.find('ul', class_='manga-list-4-list')
        div = latest_updates.find_all('li', recursive=False)

        for item in div:
            link = item.find('a')
            image = item.find('img', class_="manga-list-4-cover")['src']
            chapter = item.find('ul').find('a')
            updated = item.find('p', class_="manga-list-4-item-subtitle").find('span')

            updated = self.get_timestamp_from_string(updated.text)

            title = link['title'].replace('"', '').replace("'", '')
            
            if title != '':
                # getting image from other page
                try:
                    search = self.manganato_search(link['title'])
                    sort = [key for key in search.keys()][0]
                    image = search[sort]['image']
                except:
                    pass

                # finished getting image

                updates[title] = {
                    'link' : f"/manga_viewer?source=mangahere&id={link['href'].split('/')[-2]}",
                    'author' : 'none',
                    'image' : image,
                    'chapter' : chapter.text,
                    'chapter_link' : f"https://www.mangahere.cc{chapter['href']}",
                    'updated' : f'{updated}',
                    'source' : 'mangahere',
                    'ref' : link['href'].split('/')[-2]
                }
            
        self.dump_results('mangahere_updates', updates)

    
    def mangahere_search(self, string):
        file = requests.get(f'https://www.mangahere.cc/search?title={string.replace(" ", "+").replace("?", "").replace("!", "")}')
        doc = BeautifulSoup(file.text, 'html.parser')

        search = {}

        latest_updates = doc.find('ul', class_='manga-list-4-list')
        div = latest_updates.find_all('li', recursive=False)

        for item in div:
            link = item.find('a')
            image = item.find('img', class_="manga-list-4-cover")['src']

            ext = item.find_all('p', class_="manga-list-4-item-tip")
            author = ext[0].find('a')
            chapter = ext[1].find('a')

            # getting image from other page
            try:
                s = self.manganato_search(link['title'])
                sort = [key for key in s.keys()][0]
                image = s[sort]['image']
            except:
                pass

            # finished getting image
            
            search[link['title']] = {
                'link' : f"/manga_viewer?source=mangahere&id={link['href'].split('/')[-2]}",
                'author' : author.text if author else 'none',
                'image' : image,
                'chapter' : chapter.text,
                'chapter_link' : f"https://www.mangahere.cc{chapter['href']}",
                'updated' : None,
                'source' : 'mangahere',
                'ref' : link['href'].split('/')[-2]
            }

        return search

    def mangahere_access_manga(self, ref):
        string = self.sanitize_string('mangahere', ref)
        file = requests.get(f'https://www.mangahere.cc/manga/{string}')
        doc = BeautifulSoup(file.text, 'html.parser')

        test_404 = doc.find('div', class_='search-bar')
        if test_404:
            return None

        panel = doc.find('div', class_='detail-info-right')
        ext = panel.find('p', class_="detail-info-right-title")

        title = ext.find('span', class_='detail-info-right-title-font').text
        status = ext.find('span', class_='detail-info-right-title-tip').text

        # getting image from other page
        try:
            search = self.manganato_search(title)
            sort = [key for key in search.keys()][0]
            image = search[sort]['image']
        except Exception as e:
            image = '#'

        ext = panel.find('p', class_="detail-info-right-say")
        author = [ext.find('a').text,]

        ext = panel.find('p', class_="detail-info-right-tag-list")
        genres = ext.find_all('a')
        genres = [genre.text for genre in genres]

        description = panel.find('p', class_="fullcontent").text


        chapters_list = []
        chapter_list = doc.find('ul', class_='detail-main-list')
        try:
            chapters = chapter_list.find_all('li', recursive=False)

            for chapter in chapters:
                chapter_title = chapter.find('a')['title']
                chapter_link = f"https://www.mangahere.cc{chapter.find('a')['href']}"
                updated = chapter.find('p', class_='title2').text
                chapters_list.append({
                    'title' : chapter_title,
                    'chapter_link' : chapter_link,
                    'updated' : updated
                })
        except:
            string = self.sanitize_string('mangahere', ref)
            file = requests.get(f'https://m.mangahere.cc/manga/{string}')
            doc = BeautifulSoup(file.text, 'html.parser')

            # ext = doc.find('section', class_='main')
            # ext2 = ext.find('div', class_='table-detail')
            chapter_cage = doc.find('div', class_='manga-chapters')
            chapters = chapter_cage.find_all('li')

            for chapter in chapters:
                chapter_title = chapter.find('a').text
                chapter_link = f"{chapter.find('a')['href'].replace('//m', 'https://www')}"
                chapters_list.append({
                    'title' : chapter_title,
                    'chapter_link' : chapter_link,
                    'updated' : 'Unknown'
                })
        
        try:
            updated = doc.find('span', class_='detail-main-list-title-right').text.replace("Last Updated:", "")
        except:
            updated = 'Unknown'

        views = 'Unknown'
            
        return {
            'title' : title.replace('\n', ''),
            'image' : image,
            'author' : author,
            'status' : status,
            'genres' : genres,
            'updated' : updated,
            'views' : views,
            'description' : description.replace('<br>', ' '),
            'chapters' : chapters_list,
            'source' : 'mangahere'
        }


if __name__ == '__main__':
    # saida = MangaScrapping().mangahere_updates()
    # print(json.dumps(saida, indent = 4))

    # print(MangaScrapping().mangahere_access_manga('Star Martial God Technique'))

    auto_update = True
    auto_update_interval = 60 * 10

    while auto_update:
        MangaScrapping().routine_initialization()

        time.sleep(auto_update_interval)