# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys
sys.path.append(os.getcwd())

from manga.mangascrapping import MangaScrapping

from requests_html import HTMLSession as requests
from tools import clear




# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Mangaschan(MangaScrapping):
    def __init__(self):
        super().__init__()
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        r = requests().get('https://mangaschan.com/').html
        # r.render(sleep=1)

        updates = {}

        latest_updates = r.find('div.postbody')[0]
        latest_updates = latest_updates.find('div.listupd')[0]
        div = latest_updates.find('div.bs.styletere.stylefiv')

        for item in div:
            manga_link = item.find('a')[0]
            title = manga_link.attrs['title']
            image = manga_link.find('img')[0].attrs['src'].split('?resize')[0]

            try:
                ext = item.find('div.bigor')[0]
                ext = ext.find('ul')[0]
                ext = ext.find('li')[0]

                chapter = ext.find('a')[0]
                updated = ext.find('span')[0]
            except:
                chapter = None
                updated = None
            
            updates[title.replace('\n', '')] = {
                'link' : f'/manga_viewer?source=mangaschan&id={manga_link.attrs["href"].split("/")[-2]}',
                'author' : '',
                'image' : image,
                'chapter' : chapter.text.replace('\n', '') if chapter else '',
                'chapter_link' : chapter.attrs['href'] if chapter else '',
                'updated' : f'{self.get_timestamp_from_string(updated.text)}' if updated else '',
                'source' : 'mangaschan',
                'ref' : manga_link.attrs['href'].split('/')[-2]
            }

        self.dump_results('mangaschan_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('mangaschan', string)
        
        r = requests().get(f'https://mangaschan.com/?s={string}').html

        search = {}

        grid_result = r.find('div.postbody')[0]
        grid_result = grid_result.find('div.listupd')[0]
        div = grid_result.find('div.bs')
        print(div[0].text)

        for item in div:
            manga_link = item.find('a')[0]
            title = manga_link.attrs['title']
            image = manga_link.find('img')[0].attrs['src'].split('?resize')[0]
            
            search[title.replace('\n', '')] = {
                'link' : f'/manga_viewer?source=mangaschan&id={manga_link.attrs["href"].split("/")[-2]}',
                'author' : '',
                'image' : image,
                'chapter' : '',
                'chapter_link' : '',
                'updated' : '',
                'source' : 'mangaschan',
                'ref' : manga_link.attrs['href'].split('/')[-2]
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
    manga = Mangaschan()
    # manga = Mangaschan().latest_updates()
    print(manga.search_title('One Piece'))