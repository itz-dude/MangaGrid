# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys
sys.path.append(os.getcwd())

from manga.mangascrapping import MangaScrapping

import requests

from bs4 import BeautifulSoup

from requests_html import HTMLSession as requests


# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Manganato(MangaScrapping):
    def __init__(self):
        super().__init__()
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        r = requests().get('https://manganato.com/index.php').html
        r.render()

        updates = {}

        latest_updates = r.find('div.panel-content-homepage')[0]
        div = latest_updates.find('div.content-homepage-item')

        for item in div:
            manga_link = item.find('a')[0]
            image = manga_link.find('img')[0]
            title = item.find('h3.item-title')[0]

            try:
                author = item.find('span.item-author')[0]
            except:
                author = None

            try:
                ext = item.find('p.item-chapter')[0]
                chapter = ext.find('a')[0]
                updated = ext.find('i')[0]
            except:
                chapter = None
                updated = None
            
            updates[title.text.replace('\n', '')] = {
                'link' : f'/manga_viewer?source=manganato&id={manga_link.attrs["href"].split("/")[-1]}',
                'author' : author.text.replace('\n', '') if author else '',
                'image' : image.attrs['src'],
                'chapter' : chapter.text.replace('\n', '') if chapter else '',
                'chapter_link' : chapter.attrs['href'] if chapter else '',
                'updated' : f'{self.get_timestamp_from_string(updated.text)}' if updated else '',
                'source' : 'manganato',
                'ref' : manga_link.attrs['href'].split('/')[-1]
            }

        self.dump_results('manganato_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('manganato', string)
        
        r = requests().get(f'https://manganato.com/search/story/{string}').html
        r.render()

        search = {}

        result = r.find('div.panel-search-story')[0]
        div = result.find('div.search-story-item')

        for item in div:
            manga_link = item.find('a')[0]
            image = manga_link.find('img')[0]
            title = item.find('a.item-title')[0]
            author = item.find('span.item-author')[0]

            chapter = item.find('a.item-chapter')[0]
            updated = item.find('span.item-time')[0]
            
            search[title.text.replace('\n', '')] = {
                'link' : f'/manga_viewer?source=manganato&id={manga_link.attrs["href"].split("/")[-1]}',
                'author' : author.text.replace('\n', ''),
                'image' : image.attrs['src'],
                'chapter' : chapter.text.replace('\n', ''),
                'chapter_link' : chapter.attrs['href'],
                'updated' : updated.text.replace('\n', '')[10:],
                'source' : 'manganato',
                'ref' : manga_link.attrs['href'].split('/')[-1]
            }

        return search

    
    # def access_manga(self, ref):
    #     file = requests.get(f'https://readmanganato.com/{ref}')
    #     doc = BeautifulSoup(file.text, 'html.parser')

    #     test_404 = doc.find('div', class_='panel-not-found')
    #     if test_404:
    #         return None

    #     panel = doc.find('div', class_='panel-story-info')
    #     image = panel.find('div', class_='story-info-left').find('img')['src']

    #     panel_right = panel.find('div', class_='story-info-right')
    #     title = panel_right.find('h1').text

    #     subpanel = panel_right.find('table', class_='variations-tableInfo')
    #     ext = subpanel.find_all('tr')

    #     try:
    #         author = ext[1].find('td', class_='table-value').find_all('a')
    #         author = [a.text for a in author]
    #     except:
    #         author = []

    #     status = ext[2].find('td', class_='table-value').text

    #     try:
    #         genres = ext[3].find('td', class_='table-value').find_all('a')
    #         genres = [g.text for g in genres]
    #     except:
    #         genres = []

    #     ext = panel_right.find('div', class_='story-info-right-extent').find_all('p')

    #     updated = ext[0].find('span', class_='stre-value').text
    #     views = ext[1].find('span', class_='stre-value').text

    #     description = panel.find('div', class_='panel-story-info-description').text.replace('\nDescription :\n', '')


    #     manga_list = doc.find('div', class_='panel-story-chapter-list')
    #     chapters = manga_list.find('ul', class_='row-content-chapter').find_all('li')

    #     chapters_list = []
    #     for chapter in chapters:
    #         c_link = chapter.find('a')
    #         c_updt = chapter.find('span', class_='chapter-time')

    #         chapters_list.append({
    #             'title' : c_link.text,
    #             'chapter_link' : c_link['href'],
    #             'updated' : c_updt.text.replace('\n', '')
    #         })

            
    #     return {
    #         'title' : title.replace('\n', ''),
    #         'image' : image,
    #         'author' : author,
    #         'status' : status,
    #         'genres' : genres,
    #         'updated' : updated,
    #         'views' : views,
    #         'description' : description.replace('<br>', ' '),
    #         'chapters' : chapters_list,
    #         'source' : 'manganato'
    #     }

if __name__ == '__main__':
    manga = Manganato()
    manga = Manganato().latest_updates()
    # print(manga.search_title('One Piece'))