# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import os, sys
sys.path.append(os.getcwd())

from manga.mangascrapping import MangaScrapping
from manga.modules.manganato import Manganato

import requests

from bs4 import BeautifulSoup



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Mangahere(MangaScrapping):
    def __init__(self):
        super().__init__()
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
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
                    search = Manganato().search_title(link['title'])
                    sort = [key for key in search.keys()][0]
                    image = search[sort]['image']

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
                except:
                    pass

                # finished getting image

            
        self.dump_results('mangahere_updates', updates)

    
    def search_title(self, string):
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
                s = Manganato().search_title(link['title'])
                sort = [key for key in s.keys()][0]
                image = s[sort]['image']

                search[link['title']] = {
                    'link' : f"/manga_viewer?source=mangahere&id={link['href'].split('/')[-2]}",
                    'author' : author.text if author else '',
                    'image' : image,
                    'chapter' : chapter.text,
                    'chapter_link' : f"https://www.mangahere.cc{chapter['href']}",
                    'updated' : '',
                    'source' : 'mangahere',
                    'ref' : link['href'].split('/')[-2]
                }
            except:
                pass

            # finished getting image
            

        return search

    def access_manga(self, ref):
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
            search = Manganato().search_title(title)
            sort = [key for key in search.keys()][0]
            image = search[sort]['image']
        except Exception as e:
            pass 

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
    manga = Mangahere()
    print(manga.search_title('One Piece'))