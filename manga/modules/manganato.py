# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys
sys.path.append(os.getcwd())

from manga.mangascrapping import MangaScrapping

import requests
from bs4 import BeautifulSoup

# from requests_html import HTMLSession as requests
from tools.tools import clear

import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *


# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Manganato(MangaScrapping):
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Connection' : 'keep-alive',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Accept-Language' : 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        file = requests.get("https://manganato.com/index.php")
        doc = BeautifulSoup(file.text, 'html.parser')

        updates = {}

        latest_updates = doc.find_all('div', class_='panel-content-homepage')[0]
        div = latest_updates.find_all('div', class_='content-homepage-item')

        for item in div:
            manga_link = item.find('a')
            image = manga_link.find('img')
            title = item.find('h3', class_='item-title')

            try:
                author = item.find('span', class_='item-author')
            except:
                author = None

            try:
                ext = item.find('p', class_='item-chapter')
                chapter = ext.find('a')
                updated = ext.find('i')
            except:
                chapter = None
                updated = None
            
            updates[title.text.replace('\n', '')] = {
                'link' : f'/manga_viewer?source=manganato&id={manga_link["href"].split("/")[-1]}',
                'author' : author.text.replace('\n', '') if author else '',
                'image' : image['src'],
                'chapter' : chapter.text.replace('\n', '') if chapter else '',
                'chapter_link' : chapter['href'] if chapter else '',
                'updated' : f'{self.get_timestamp_from_string(updated.text)}' if updated else '',
                'source' : 'manganato',
                'ref' : manga_link['href'].split('/')[-1]
            }

        self.dump_results('manganato_updates', updates)


    def search_title(self, string):
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
                'author' : author.text.replace('\n', '') if author else '',
                'image' : image['src'],
                'chapter' : chapter.text.replace('\n', ''),
                'chapter_link' : f"chapter_viewer?source=manganato&id={'___'.join(chapter['href'].split('/')[-2:])}",
                'updated' : updated.text.replace('\n', '')[10:] if updated else '',
                'source' : 'manganato',
                'ref' : manga_link['href'].split('/')[-1]
            }

        return search

    
    def access_manga(self, ref):
        file = requests.get(f'https://readmanganato.com/{ref}')
        doc = BeautifulSoup(file.text, 'html.parser')

        test_404 = doc.find('div', class_='panel-not-found')
        if test_404:
            return None

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
                'chapter_link' : f"chapter_viewer?source=manganato&id={'___'.join(c_link['href'].split('/')[-2:])}",
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

    def get_chapter_content(self, ref):
        link = f'https://readmanganato.com/{"/".join(ref.split("___"))}'
        file = requests.get(link, headers=self.headers)
        doc = BeautifulSoup(file.text, 'html.parser')

        test_404 = doc.find('div', class_='panel-not-found')
        if test_404:
            return None

        title = doc.find('div', class_='panel-chapter-info-top').find('h1').text
        title = ' '.join([t.capitalize() for t in title.split()])

        content = doc.find('div', class_='container-chapter-reader')
        content = content.find_all('img')

        print(requests.get(content[0]['src']).content)

        prev_link = doc.find('a', class_='navi-change-chapter-btn-prev')
        next_link = doc.find('a', class_='navi-change-chapter-btn-next')

        return {
            'title' : title.replace('\n', ''),
            'prev_chapter' : prev_link['href'] if prev_link else '',
            'next_chapter' : next_link['href'] if next_link else '',
            'chapters' : [p.attrs['src'] for p in content]
        }

    def get_chapter_content_a(self, ref):
        self.browser(self.debug)
        self.driver.get(f'https://readmanganato.com/{"/".join(ref.split("___"))}')

        # getting title and chapter
        title = self.waiting(self.driver, By.CLASS_NAME, 'panel-breadcrumb')
        title = self.waiting(title, By.CLASS_NAME, 'a-h', plural=True)
        chapter = [i for i in title[-1].text.replace(':', '').split(' ') if i.isdigit()][0]
        title_raw = title
        title = self.sanitize_string('manganato', title[-2].text)

        # checking local folder
        relation = ''
        response = self.creating_manga_and_chapter_folder(title, chapter)
        if response[1]:
            try:
                prev_link = self.waiting(self.driver, By.CLASS_NAME, 'navi-change-chapter-btn-prev')
            except: # if there is no previous chapter
                prev_link = None
            try:
                next_link = self.waiting(self.driver, By.CLASS_NAME, 'navi-change-chapter-btn-next')
            except: # if there is no next chapter
                next_link = None

            content = self.waiting(self.driver, By.CLASS_NAME, 'container-chapter-reader')
            content = self.waiting(content, By.TAG_NAME, 'img', plural=True)

            img_saved = []
            for index, img in enumerate(content):
                img_data = img.screenshot_as_png
                with open(f'static/manga/results/{title}/{chapter}/id-{index}.png', 'wb') as f:
                    f.write(img_data)
                img_saved.append(f'static/manga/results/{title}/{chapter}/id-{index}.png')

            relation = {
                'imgs': img_saved,
                'prev': prev_link.get_attribute('href') if prev_link else '#',
                'next': next_link.get_attribute('href') if next_link else '#'
            }

            with open(f'static/manga/results/{title}/{chapter}/relation.json', 'w') as f:
                json.dump(relation, f)

        else:
            # open relation json and get the relation for the chapter
            with open(f'static/manga/results/{title}/{chapter}/relation.json', 'r') as f:
                relation = json.load(f)

        return {
            'title' : title_raw,
            'prev_chapter' : relation['prev'],
            'next_chapter' : relation['next'],
            'chapters' : relation['imgs']
        }
            


if __name__ == '__main__':
    clear()
    
    manga = Manganato()
    manga = Manganato().get_chapter_content_a('manga-bb979136___chapter-1')
    # print(manga)
    # print(manga.search_title('One Piece'))