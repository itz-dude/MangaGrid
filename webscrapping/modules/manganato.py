# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

from webscrapping.mangascrapping import MangaScrapping

import requests

from bs4 import BeautifulSoup



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Manganato(MangaScrapping):
    def __init__(self):
        super().__init__()
        
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
                'author' : author.text.replace('\n', ''),
                'image' : image['src'],
                'chapter' : chapter.text.replace('\n', ''),
                'chapter_link' : chapter['href'],
                'updated' : updated.text.replace('\n', '')[10:],
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