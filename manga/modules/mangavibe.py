# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys, datetime
from time import sleep
sys.path.append(os.getcwd())

from requests_html import HTMLSession as requests

from manga.mangascrapping import MangaScrapping
from tools.tools import clear



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

    
    def access_manga(self, ref):
        r = requests().get(f'https://mangavibe.top/manga/{"/".join(ref.split("___"))}').html
        r.render(sleep=1.5)

        test_404 = r.find('div.text-center.mx-17')
        if len(test_404) > 0 and test_404[0].text == 'Essa página não existe':
            return None

        image = f'https://cdn.mangavibe.top/img/media/{ref.split("___")[0]}/cover/l.jpg'

        ext = r.find('div#media-info-desktop')[0]
        title = ext.find('div.mt-0')[0].text

        genres = ext.find('div.my-17')[0]
        genres = genres.find('button')
        if len(genres) > 0:
            genres = [genre.text for genre in genres]
        else:
            genres = []

        author = []
        status = ext.find('div')[10].text.replace('Status: ', '')
        views = ''
        description = ext.find('div')[-1].text.replace('Sinopse: ', '')

        chapter_grid = r.find('div#item-collection')[0]
        chapters = chapter_grid.find('a')

        updated = chapters[-1].find('div')[0].text
        updated = f'0{updated}' if len(updated) < 10 else updated
        try:
            updated = datetime.datetime.strptime(updated, '%m/%d/%Y')
            updated = self.get_string_from_timestamp(updated)
        except: updated = ''

        chapters_list = []
        for chapter in chapters[::-1]:
            c_link = chapter.attrs['href']

            c_updt = chapter.find('div')[0].text
            c_updt = f'0{c_updt}' if len(c_updt) < 10 else c_updt
            try: c_updt = datetime.datetime.strptime(c_updt, '%m/%d/%Y')
            except: c_updt = ''
            c_updt = self.get_string_from_timestamp(c_updt)
            
            c_title = chapter.find('div')[1].text

            chapters_list.append({
                'title' : c_title,
                'chapter_link' : f'https://mangavibe.top{c_link}',
                'updated' : c_updt
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
            'source' : 'mangavibe'
        }

if __name__ == '__main__':
    clear()
    print(Mangavibe().access_manga('13773___renai-flops'))