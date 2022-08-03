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


class Mangatoo(MangaScrapping):
    def __init__(self):
        super().__init__()
        self.source = 'mangatoo'

    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        r = requests().get('https://mangatoo.net/').html
        # r.render(sleep=3)

        updates = {}

        latest_updates = r.find('div#loop-content')[0]
        div = latest_updates.find('div.page-item-detail.text')

        for item in div:
            manga_link = item.find('a')[0]
            title = item.find('h3')[0].text

            try:
                image = item.find('img')[0].attrs['data-src']
            except:
                image = item.find('img')[0].attrs['src']

            chapter = item.find('a')[2]
            updated = 'unknown'

            updates[title.replace('\n', '').replace('HOT ', '')] = {
                'link' : self.link_manga_viewer(manga_link.attrs["href"].split("/")[-2]),
                'author' : '',
                'image' : image,
                'chapter' : chapter.text.replace('\n', '') if chapter else '',
                'chapter_link' : self.link_chapter_viewer(chapter.attrs['href'].split('/')[-2]),
                'updated' : f'{self.get_timestamp_from_string(updated, self.source)}',
                'source' : self.source,
                'slug' : manga_link.attrs['href'].split('/')[-2]
            }

        self.dump_results(f'{self.source}_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('mangaschan', string)
        r = requests().get(f'https://mangatoo.net/?s={string}&post_type=wp-manga').html

        search = {}

        grid_result = r.find('div.c-tabs-item')[0]
        div = grid_result.find('div.c-tabs-item__content')

        for item in div:
            manga_link = item.find('a')[0]
            title = item.find('h3')[0].text

            try:
                image = item.find('img')[0].attrs['data-src']
            except:
                image = item.find('img')[0].attrs['src']

            chapter = item.find('span.font-meta.chapter')[0].find('a')[0]
            chapter_link = chapter.attrs['href']

            updated = item.find('div.meta-item.post-on')[0]
            updated = updated.text if updated.find('a') == None else f'{datetime.datetime.now()}'

            search[title.replace('\n', '')] = {
                'link' : self.link_manga_viewer(manga_link.attrs["href"].split("/")[-2]),
                'author' : '',
                'image' : image,
                'chapter' : chapter.text,
                'chapter_link' : self.link_chapter_viewer(chapter_link.split('/')[-2]),
                'updated' : self.get_date_from_string(updated),
                'source' : self.source,
                'slug' : manga_link.attrs['href'].split('/')[-2]
            }

        return search


    def access_manga(self, slug):
        r = requests().get(f'https://mangatoo.net/manga/{slug}').html
        r.render(sleep=2)

        test_404 = r.find('div.notf')
        if test_404:
            return 'not found'

        title = r.find('div.profile-manga')[0].find('div.post-title')[0].text

        try:
            author = r.find('div.author-content')[0].text
            author = author.split(',') if isinstance(author.split(','), list) else [author,]
        except:
            author = []

        description = r.find('div.description-summary')[0].text.replace(' Show more ', '').replace('\xa0', ' ').replace('\n', ' ')

        updated = r.find('ul.version-chap')[0].find('li')[0].find('span.chapter-release-date')[0]
        updated = updated.text if updated.find('a') == None else f'{datetime.datetime.now()}'

        status = r.find('div.post-status')[0].find('div.summary-content')[0].text
        views = ''

        genres = r.find('div.genres-content')[0].find('a')
        genres = [genre.text for genre in genres]

        try:
            image = r.find('div.summary_image')[0].find('img')[0].attrs['data-src']
        except:
            image = r.find('div.summary_image')[0].find('img')[0].attrs['src']

        chapter_list = r.find('ul.version-chap')[0].find('li')

        ch_list = []
        for chapter in chapter_list:
            c_link = chapter.find('a')[0]
            c_title = c_link.text
            c_updt = chapter.find('span.chapter-release-date')[0]
            c_updt = c_updt.text.replace(',', '').replace(' ', '/') if not c_updt.find('a') else f'{datetime.datetime.now()}'
            try:
                c_updt = self.get_date_from_string(c_updt)
            except:
                c_updt = self.get_timestamp_from_string(c_updt, 'mangatoo')

            ch_list.append({
                'title' : c_title.replace(title, ''),
                'slug' : f"{c_link.attrs['href'].split('/')[-3]}___{c_link.attrs['href'].split('/')[-2]}",
                'chapter_link' : self.link_chapter_viewer(f"{c_link.attrs['href'].split('/')[-3]}___{c_link.attrs['href'].split('/')[-2]}"),
                'updated' : c_updt
            })

        return {
            'title' : title.replace('\n', ''),
            'image' : image,
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
        r = requests().get(f'https://mangatoo.net/manga/{slug.replace("___","/")}').html
        # r.render(sleep=0.2)

        # test_404 = r.find('div.notf')
        # if test_404:
        #     return 'not found'

        # title = r.find('div.wrapper')[0]
        title = r.find('h1#chapter-heading')[0].text

        content = r.find('div.main-col-inner')[0].find('div.reading-content')[0]
        content = content.find('img')


        # discovering previous and next chapter
        container = r.find('div.nav-links')[0]
        prev_link = container.find('a.prev_page')
        if prev_link:
            prev_link = prev_link[0].attrs['href']
        else:
            prev_link = '#'

        next_link = container.find('a.next_page')
        if next_link:
            next_link = next_link[0].attrs['href']
        else:
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
            'chapters' : [p.attrs['src'] for p in content]
        }

if __name__ == '__main__':
    manga = Mangatoo()
    # manga.latest_updates()
    # print(manga.search_title('i became a crow'))
    # print(manga.access_manga('why-she-lives-as-a-villainess'))
    print(manga.get_chapter_content('why-she-lives-as-a-villainess___chapter-35'))
    # print(manga.get_chapter_content('osabori-jouzuna-koumukai-san-wa-ore-wo-nogasanai-capitulo-2'))