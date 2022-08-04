# -------------------- SELF RUN ------------------- #
# make the script return to the main directory
import os, sys

sys.path.append(os.getcwd())


# ---------------- DEFAULT IMPORTS ---------------- #
import datetime

from manga.mangascrapping import MangaScrapping

from requests_html import HTMLSession as requests
from tools.tools import pprint

from manga.models import Chapters, Mangas

# ------------------- STRUCTURE ------------------- #


class Mangadex(MangaScrapping):
    def __init__(self):
        super().__init__()
        self.source = 'mangadex'

    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        r = requests().get('https://mangadex.tv/').html

        updates = {}

        latest_updates = r.find('div.row.m-0')[0]
        div = latest_updates.find('div.col-md-6')

        for item in div:
            manga_link = item.find('a.manga_title')[0]
            title = manga_link.text

            try:
                image = item.find('img')[0].attrs['data-src']
            except:
                image = item.find('img')[0].attrs['src']

            chapter = item.find('a')[2]
            updated = 'unknown'

            updates[title] = {
                'link' : self.link_manga_viewer(manga_link.attrs["href"].split("/")[-1]),
                'author' : '',
                'image' : f'https://mangadex.tv/{image}',
                'chapter' : chapter.text.replace('\n', '') if chapter else '',
                'chapter_link' : self.link_chapter_viewer(f'{chapter.attrs["href"].split("/")[-2]}___{chapter.attrs["href"].split("/")[-1]}'),
                'updated' : f'{self.get_timestamp_from_string(updated, self.source)}',
                'source' : self.source,
                'slug' : manga_link.attrs['href'].split('/')[-1]
            }

        self.dump_results(f'{self.source}_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('mangaschan', string)
        r = requests().get(f'https://mangadex.tv/search?type=titles&title={string}&submit=').html

        search = {}

        grid_result = r.find('div.row.mt-1.mx-0')[0]
        div = grid_result.find('div.manga-entry')

        for item in div:
            manga_link = item.find('a.manga_title')[0]
            title = manga_link.text

            try:
                image = item.find('img')[0].attrs['data-src']
            except:
                image = item.find('img')[0].attrs['src']

            chapter = ''
            chapter_link = ''

            updated = 'unknown'

            search[title.replace('\n', '')] = {
                'link' : self.link_manga_viewer(manga_link.attrs["href"].split("/")[-1]),
                'author' : '',
                'image' : f'https://mangadex.tv/{image}',
                'chapter' : '',
                'chapter_link' : '',
                'updated' : self.get_date_from_string(updated),
                'source' : self.source,
                'slug' : manga_link.attrs['href'].split('/')[-1]
            }

        return search


    def access_manga(self, slug):
        r = requests().get(f'https://mangadex.tv/manga/{slug}').html
        # r.render(sleep=2)

        test_404 = r.find('div.notf')
        if test_404:
            return 'not found'

        title = r.find('h6.card-header')[0].text  #.find('span.mx1')[0]

        ext = r.find('div.col-xl-9.col-lg-8.col-md-7')[0].find('div.row')

        author = ext[2].find('a')
        author = [a.text for a in author]

        description = ext[-1].find('div')[-1].text

        # updated = r.find('div.chapter-container')[0].find('div.row.no-gutters')[3].find('div')[6].text
        # updated = updated.replace(',',' ').replace(' ','/') if updated != None else 'unknown'
        # try:
        #     updated = self.get_date_from_string(updated)
        # except:
        #     updated = self.get_timestamp_from_string(updated, 'mangadex')
        updated = 'unknown'

        status = ext[5].find('div')[-1].text
        views = ext[6].find('ul')[0].find('li')[0].text

        genres = ext[3].find('a ')
        genres = [genre.text for genre in genres]

        try:
            image = r.find('div.col-xl-3.col-lg-4.col-md-5')[0].find('img')[0].attrs['data-src']
        except:
            image = r.find('div.col-xl-3.col-lg-4.col-md-5')[0].find('img')[0].attrs['src']

        chapter_list = r.find('div.chapter-container')[0].find('div.row.no-gutters')

        ch_list = []
        for chapter in chapter_list[3:]:
            c_link = chapter.find('a')[0]
            c_title = c_link.text
            # c_updt = c_updt.replace(',',' ').replace(' ','/') if c_updt != None else 'unknown'
            c_updt = 'unknown'

            ch = {
                'title' : c_title.replace(title, ''),
                'slug' : f"{c_link.attrs['href'].split('/')[-2]}___{c_link.attrs['href'].split('/')[-1]}",
                'chapter_link' : self.link_chapter_viewer(f"{c_link.attrs['href'].split('/')[-2]}___{c_link.attrs['href'].split('/')[-1]}"),
                'updated' : self.get_date_from_string(c_updt)
            }

            if ch not in ch_list:
                ch_list.append(ch)

        return {
            'title' : title,
            'image' : f'https://mangadex.tv/{image}',
            'author' : author,
            'status' : status,
            'genres' : genres,
            'updated' : self.get_date_from_string(updated),
            'views' : views,
            'description' : description.replace('<br>', ' '),
            'chapters' : ch_list,
            'source' : self.source,
            'slug' : slug
        }

    def get_chapter_content(self, slug):
        r = requests().get(f'https://mangadex.tv/chapter/{slug.replace("___","/")}').html
        # r.render(sleep=0.2)

        # test_404 = r.find('div.notf')
        # if test_404:
        #     return 'not found'

        # title = r.find('div.wrapper')[0]
        title = r.find('a.manga-link')[0].text

        content = r.find('div.reader-images')[0]
        content = content.find('img')

        images = []
        for image in content:
            try:
                images.append(image.attrs['data-src'])
            except:
                images.append(image.attrs['src'])


        # discovering previous and next chapter
        container = r.find('div.reader-controls-chapters')[0]
        prev_link = container.find('a.chapter-link-left')
        try:
            prev_link = prev_link[0].attrs['href']
            prev_link = self.link_chapter_viewer(f'{prev_link.split("/")[-2]}___{prev_link.split("/")[-1]}')
        except:
            prev_link = '#'

        next_link = container.find('a.chapter-link-right')
        try:
            next_link = next_link[0].attrs['href']
            next_link = self.link_chapter_viewer(f'{next_link.split("/")[-2]}___{next_link.split("/")[-1]}')
        except:
            next_link = '#'

        try:
            manga = Mangas.query.join(Chapters).filter(Chapters.slug==slug).first()
            manga_title = manga.title
            manga_page = self.link_manga_viewer(manga.slug)
        except Exception as e:
            print(e)
            pprint(f'[i] {self.source.capitalize()}/get_chapter_content - Manga not found in database', 'yellow')
            manga_title = ''
            manga_page = '#'

        return {
            'manga_title' : manga_title,
            'manga_page' : manga_page,
            'title' : title.replace(manga_title, '').replace('\n', ''),
            'prev_chapter' : prev_link,
            'next_chapter' : next_link,
            'chapters' : images
        }

if __name__ == '__main__':
    manga = Mangadex()
    # manga.latest_updates()
    # print(manga.search_title('i became a crow'))
    # print(manga.search_title('Confidential Assassination Troop'))
    # print(manga.access_manga('manga-tk952067'))
    print(manga.get_chapter_content('manga-dv981004___chapter-1'))
    # print(manga.get_chapter_content('osabori-jouzuna-koumukai-san-wa-ore-wo-nogasanai-capitulo-2'))