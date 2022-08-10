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


class GoldenMangas(MangaScrapping):
    def __init__(self):
        super().__init__()
        self.source = 'goldenmangas'
        self.source_lang = 'pt_BR'
        self.source_url = 'https://goldenmangas.top'

    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        r = requests().get(self.source_url).html

        updates = {}

        latest_updates = r.find('div#response')[0].find('div.atualizacao')

        for item in latest_updates:
            manga_link = item.find('a')[0]
            manga_link = manga_link.attrs['href'].split('/')[-1]

            first_part = item.find('div.col-sm-2')[0]
            image = first_part.find('img')[0].attrs['src'].split('&')[0] + '&w=500'

            second_part = item.find('div.col-sm-10')[0]
            title = second_part.find('h3')[0].text
            
            chapter_ext = second_part.find('a.label-success')[0]
            chapter = chapter_ext.text
            chapter_link = self.link_chapter_viewer(f'{chapter_ext.attrs["href"].split("/")[-2]}___{chapter_ext.attrs["href"].split("/")[-1]}')

            updated = second_part.find('div.dataAtualizacao')[0].text
            updated = datetime.datetime.strptime(updated, '%d/%m/%Y')

            updates[title] = {
                'link' : self.link_manga_viewer(manga_link),
                'author' : '',
                'image' : f'{self.source_url}/{image}',
                'chapter' : chapter,
                'chapter_link' : chapter_link,
                'updated' : str(updated),
                'source' : self.source,
                'source_lang' : self.source_lang,
                'source_url' : self.source_url,
                'slug' : manga_link
            }

        self.dump_results(f'{self.source}_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('mangaschan', string)
        r = requests().get(f'{self.source_url}/mangabr?busca={string}').html

        search = {}

        grid_result = r.find('section.row')[0].find('div.mangas ')

        for item in grid_result:
            manga_link = item.find('a')[0].attrs['href'].split('/')[-1]
            title = item.find('h3')[0].text
            image = item.find('img')[0].attrs['src'].split('&')[0] + '&w=500'

            search[title.replace('\n', '')] = {
                'link' : self.link_manga_viewer(manga_link),
                'author' : '',
                'image' : f'{self.source_url}/{image}',
                'chapter' : '',
                'chapter_link' : '',
                'updated' : self.get_date_from_string('unknown'),
                'source' : self.source,
                'source_lang' : self.source_lang,
                'source_url' : self.source_url,
                'slug' : manga_link
            }

        return search


    def access_manga(self, slug):
        r = requests().get(f'{self.source_url}/mangabr/{slug}').html

        ext = r.find('div.row')[1]
        title = ext.find('h2')[0].text

        if title == '':
            return 'not found'

        image = ext.find('img')[0].attrs['src'].split('&')[0] + '&w=500'

        fields = ext.find('h5.cg_color')
        fields = {
            field.find('strong')[0].text.replace(':','') : [a.text for a in field.find('a') if a.text != ''] for field in fields
        }

        author = fields.get('Autor')
        status = fields.get('Status')[0]
        genres = fields.get('Genero')

        updated = r.find('ul#capitulos')[0].find('li')[0].find('span')[0].text.replace('(', '').replace(')', '')
        updated = datetime.datetime.strptime(updated, '%d/%m/%Y')

        views = ''
        description = r.find('div#manga_capitulo_descricao')[0].text.replace('\n', ' ').replace('<br>', ' ')

        chapter_list = r.find('ul#capitulos')[0].find('li')

        ch_list = []
        for chapter in chapter_list:
            c_link = chapter.find('a')[0].attrs['href'].split('/')[-1]

            c_updt = chapter.find('span')[0].text
            c_title = chapter.find('a > div')[0].text.replace(c_updt, '').strip()

            c_updt = datetime.datetime.strptime(c_updt.replace('(', '').replace(')', ''), '%d/%m/%Y')
            

            ch_list.append({
                'title' : c_title,
                'slug' : f"{slug}___{c_link}",
                'chapter_link' : self.link_chapter_viewer(f'{slug}___{c_link}'),
                'updated' : c_updt
            })

        return {
            'title' : title,
            'image' : f'{self.source_url}/{image}',
            'author' : author,
            'status' : status,
            'genres' : genres,
            'updated' : updated,
            'views' : views,
            'description' : description,
            'chapters' : ch_list,
            'source' : self.source,
            'source_lang' : self.source_lang,
            'source_url' : self.source_url,
            'slug' : slug
        }

    def get_chapter_content(self, slug):
        r = requests().get(f'{self.source_url}/mangabr/{slug.replace("___","/")}').html

        title = f'Capítulo {slug.split("___")[1]}'

        try:
            content = r.find('div#capitulos_images')[0].find('img')

            images = []
            for image in content:
                images.append(f'{self.source_url}{image.attrs["src"]}')


            # discovering previous and next chapter
            select_chapter = r.find('select#capitulo_trocar')[0]
            options = [s.text for s in select_chapter.find('option')]
            option_selected = select_chapter.find('option[selected]')[0].text

            prev_link = ''
            next_link = ''
            
            if options.index(option_selected) == 0:
                prev_link = '#'
                
                next_link = options[options.index(option_selected) + 1]
                next_link = self.link_chapter_viewer(f'{slug.split("___")[0]}___{next_link}')

            elif options.index(option_selected) != 0 and options.index(option_selected) != len(options) - 1:
                prev_link = options[options.index(option_selected) - 1]
                prev_link = self.link_chapter_viewer(f'{slug.split("___")[0]}___{prev_link}')

                next_link = options[options.index(option_selected) + 1]
                next_link = self.link_chapter_viewer(f'{slug.split("___")[0]}___{next_link}')

            else:
                prev_link = options[options.index(option_selected) - 1]
                prev_link = self.link_chapter_viewer(f'{slug.split("___")[0]}___{prev_link}')

                next_link = '#'

            try:
                manga = Mangas.query.join(Chapters).filter(Chapters.slug==slug).first()
                manga_title = manga.title
                manga_page = self.link_manga_viewer(manga.slug)
            except Exception as e:
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

        except:
            return 'not found'

if __name__ == '__main__':
    manga = GoldenMangas()
    # manga.latest_updates()
    # print(manga.search_title('i became a crow'))
    # print(manga.search_title('Confidential Assassination Troop'))
    print(manga.access_manga('regressor-instruction-manual'))
    # print(manga.get_chapter_content('regressor-instruction-manual___54'))