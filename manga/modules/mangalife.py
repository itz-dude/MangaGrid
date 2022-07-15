# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import os, sys
sys.path.append(os.getcwd())

from manga.mangascrapping import MangaScrapping

import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import *



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Mangalife(MangaScrapping):
    def __init__(self):
        super().__init__()
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
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


    def search_title(self, string):
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


if __name__ == '__main__':
    manga = Mangalife()
    print(manga.search_title('One Piece'))