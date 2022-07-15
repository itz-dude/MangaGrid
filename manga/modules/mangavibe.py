# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys
from time import sleep
sys.path.append(os.getcwd())

from requests_html import HTMLSession as requests

from manga.mangascrapping import MangaScrapping
from tools import clear



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Mangavibe(MangaScrapping):
    def __init__(self):
        super().__init__()
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        first = requests().get('https://mangavibe.top/mangas?Ordem=Atualizados').html
        first.render(sleep=1)
        secnd = requests().get('https://mangavibe.top/mangas/2?Ordem=Atualizados').html
        secnd.render(sleep=1)

        updates = {}

        for page in [first, secnd]:

            latest_updates = page.find('div.MuiGrid-container')[-1]
            div = latest_updates.find('div.MuiGrid-item')

            for item in div:
                manga_link = item.find('a')[0]
                image = f"https://cdn.mangavibe.top/img/media/{manga_link.attrs['href'].split('/')[2]}/cover/m.jpg"
                title = item.find('div.MuiCardContent-root')[0].find('span')[0].text
                author = None

                try:
                    ext = item.find('div.d-flex.position-absolute.m-7')[0].find('span')
                    chapter = f'{ext[1].text} {ext[0].text}'
                except:
                    chapter = None

                updated = None

                if updates.get(title):
                    if updates[title].get('chapter') > chapter:
                        continue
                
                updates[title] = {
                    'link' : f'/manga_viewer?source=mangavibe&id={manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}',
                    'author' : '',
                    'image' : image,
                    'chapter' : chapter,
                    'chapter_link' : f'https://mangavibe.top{manga_link.attrs["href"]}',
                    'updated' : '',
                    'source' : 'mangavibe',
                    'ref' : f'{manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}'
                }

        self.dump_results('mangavibe_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('manganato', string)
        
        r = requests().get(f'https://mangavibe.top/mangas?s={string}').html
        r.render(sleep=1)

        search = {}

        latest_updates = r.find('div.MuiGrid-container')[-1]
        div = latest_updates.find('div.MuiGrid-item')

        for item in div:
            manga_link = item.find('a')[0]
            image = f"https://cdn.mangavibe.top/img/media/{manga_link.attrs['href'].split('/')[2]}/cover/m.jpg"
            title = item.find('div.MuiCardContent-root')[0].find('span')[0].text
            author = None

            try:
                ext = item.find('div.d-flex.position-absolute.m-7')[0].find('span')
                chapter = f'{ext[1].text} {ext[0].text}'
            except:
                chapter = None

            updated = None

            if search.get(title):
                if search[title].get('chapter') > chapter:
                    continue
            
            search[title] = {
                'link' : f'/manga_viewer?source=mangavibe&id={manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}',
                'author' : '',
                'image' : image,
                'chapter' : chapter if chapter else '',
                'chapter_link' : f'https://mangavibe.top{manga_link.attrs["href"]}',
                'updated' : '',
                'source' : 'mangavibe',
                'ref' : f'{manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}'
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
    clear()
    manga = Mangavibe().search_title('god')
    print(manga)
    # print(manga.search_title('One Piece'))