# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

import datetime
import json
import os
import sys
from turtle import update

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *

from extensions import db
from tools.tools import clear, pprint

from manga.models import Genres, Sources, Mangas, Status, Authors, Chapters
from users.models import Users, History, Favorites, Notifications

# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class MangaScrapping():

    def __init__(self):
        self.debug = False
        self.source = None

        self.string_ts = {
            'seconds' : ['sec', 'seconds', 'second', 'secs', 'segundos', 'seg'],
            'minutes' : ['min', 'minutes', 'minut', 'mins', 'minutos', 'min'],
            'hours' : ['hour', 'hours', 'horas', 'hora', 'hrs'],
            'days' : ['day', 'days', 'dias', 'dia'],
            'weeks' : ['week', 'weeks', 'semanas', 'semana'],
            'months' : ['month', 'months', 'meses', 'mes'],
            'years' : ['year', 'years', 'anos', 'ano'],
        }

        self.string_ts2 = {
            '01' : ['Jan', 'jan', 'January', 'january', 'Janeiro', 'janeiro'],
            '02' : ['Feb', 'Februari', 'Februari', 'Fevereiro', 'fevereiro'],
            '03' : ['Mar', 'Mar', 'March', 'mar', 'Março', 'março'],
            '04' : ['Apr', 'April', 'April', 'Abril', 'abril'],
            '05' : ['May', 'Mei', 'May', 'Mai', 'Maio', 'maio'],
            '06' : ['Jun', 'Juni', 'June', 'jun', 'Junho', 'junho'],
            '07' : ['Jul', 'Juli', 'July', 'jul', 'Julho', 'julho'],
            '08' : ['Aug', 'Aug', 'August', 'aug', 'Agosto', 'agosto'],
            '09' : ['Sep', 'Sep', 'September', 'sep', 'Setembro', 'setembro'],
            '10' : ['Oct', 'Okt', 'October', 'oct', 'Outubro', 'outubro'],
            '11' : ['Nov', 'Nov', 'November', 'nov', 'Novembro', 'novembro'],
            '12' : ['Dec', 'Des', 'December', 'dec', 'Dezembro', 'dezembro'],
        }

    @property
    def driver_path(self):
        if sys.platform == 'linux':
            return '/usr/bin/geckodriver'
        elif sys.platform == 'win32':
            return 'manga/chromedriver.exe'


    # ------------------------------------------------- #
    # -------------------- TOOLS ---------------------- #
    # ------------------------------------------------- #

    def waiting(self, driver, tag = By.XPATH, tag_name = '', plural = False):
        if plural:
            return WebDriverWait(driver, 20).until(ec.presence_of_all_elements_located((tag, tag_name)))
        else:
            return WebDriverWait(driver, 20).until(ec.presence_of_element_located((tag, tag_name)))


    def browser(self, showing = False):
        if sys.platform == 'linux':
            c = DesiredCapabilities.FIREFOX
            c["pageLoadStrategy"] = "none"
            self.driver = webdriver.Firefox(service=Service(self.driver_path), desired_capabilities=c)

        elif sys.platform == 'win32':
            c = DesiredCapabilities.CHROME
            options = Options()
            if not showing:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(service=Service(self.driver_path), desired_capabilities=c, options=options)
            self.driver.minimize_window()


    def get_timestamp_from_string(self, string, where = 'all'):
        output = {}

        if where in ['mangaschan']:
            string = string.replace(',', '').split(' ')
        elif where in ['mangatoo', 'mangadex']:
            string = string.replace(',', '').split('/')
        else:
            string = string.replace(',', '').split(' ')
            if 'an' in string:
                string[string.index('an')] = '1'
            elif 'An' in string:
                string[string.index('An')] = '1'

        for time in self.string_ts.keys():
            for param in self.string_ts[time]:
                if param in string:
                    output[time] = int(string[string.index(param) - 1])
                    return datetime.datetime.now() - datetime.timedelta(**output)

        for month in self.string_ts2.keys():
            for param in self.string_ts2[month]:
                if param in string:
                    output['month'] = int(month)
                    output['day'] = int(string[string.index(param) + 1].replace(',', ''))
                    try:
                        if where == 'mangadex':
                            output['year'] = int(string[string.index(param) + 2]) + 2000
                        else:
                            output['year'] = int(string[string.index(param) + 2])
                    except:
                        output['year'] = int(datetime.datetime.now().year) if output['month'] < int(datetime.datetime.now().month) else int(datetime.datetime.now().year) - 1
                        output['hour'] = int(string[-1].split(':')[0])
                        output['minute'] = int(string[-1].split(':')[1])

                    return datetime.datetime(**output)

        # raise Exception('Timestamp not found')
        return datetime.datetime(year=2010, month=1, day=1)


    def get_date_from_string(self, string):
        datetime_expected = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y'
        ]

        for format in datetime_expected:
            try:
                return datetime.datetime.strptime(string, format)
            except:
                pass

        if string == 'unknown':
            return datetime.datetime(year=2010, month=1, day=1)

        raise Exception('Date not found')


    def get_string_from_timestamp(self, timestamp):
        """
        This function will receive a time stamp and the output will be:
        'X secs ago', 'X hours ago' or 'X days ago'.
        """
        now = datetime.datetime.now()
        delta = now - timestamp

        if delta.days == 0:
            return 'Today'
        elif delta.days == 1:
            return 'Yesterday'
        elif delta.days < 7:
            return f'{delta.days} days ago'
        elif delta.days < 30:
            return f'{int(delta.days / 7)} weeks ago'
        elif delta.days < 365:
            return f'{int(delta.days / 30)} months ago'
        elif delta.days < 365 * 10:
            return f'{int(delta.days / 365)} year ago'
        else:
            return 'Unknown'



    def dump_results(self, archive, results):
        with open(f"manga/results/{archive}.json", "w") as mangas:
            mangas.write(json.dumps(results, indent = 4))

        pprint(f'[!] LOG: Results saved {archive}.json', 'green')

    def sanitize_string(self, source, string):
        dic = {
            'manganato' : {
                "_" : [" ", "'", ",", "-"],
                "" : ["?", "!", '"', ".", "~"],
            },
            'mangahere' : {
                "_" : [" ", "-"],
                "" : [":", "!", "?", ";", ",", "."],
            },
            'mangaschan' : {
                "%21" : ["!",],
                "%3F" : ["?",],
                "%2C" : [",",],
                "%2F" : ["/",],
                "%2D" : ["-",],
                "%27" : ["'",],
                "%3A" : [":",],
                "%3B" : [";",],
                "%3D" : ["=",],
                "%2B" : ["+",],
                "%2A" : ["*",],
                "%25" : ["%",],
                "%7C" : ["|",],
                "+" : [" ",],
            }
        }

        for key in dic[source].keys():
            for value in dic[source][key]:
                string = string.replace(value, key)

        return string.lower()

    def creating_manga_and_chapter_folder(self, manga, chapter):
        fmanga, fchapter = False, False
        if not os.path.exists(f'static/manga/results/{manga}'):
            os.makedirs(f'static/manga/results/{manga}')
            fmanga = True
        if not os.path.exists(f'static/manga/results/{manga}/{chapter}'):
            os.makedirs(f'static/manga/results/{manga}/{chapter}')
            open(f'static/manga/results/{manga}/{chapter}/relation.json', 'w').close()
            fchapter = True

        return [fmanga, fchapter]

    def link_manga_viewer(self, slug):
        return f'/manga_viewer?source={self.source}&id={slug}'

    def link_chapter_viewer(self, slug):
        return f'/chapter_viewer?source={self.source}&id={slug}'

    # -------------------- INDEXING BEHAVIORS -------------------- #
    def idx_manga(self, manga: dict):
        source = self.idx_source(manga['source'], manga['source_lang'], manga['source_url'])
        status = self.idx_status(manga['status'])

        authors =  [self.idx_author(author) for author in manga['author']]
        genres =  [self.idx_genre(genre) for genre in manga['genres']]
            
        manga_obj = self.idx_manga_title(manga, {'source':source, 'status':status})

        for author in authors:
            if author not in manga_obj.author:
                manga_obj.author.append(author)
                pprint(f'[!] Info: Author {author.slug} added to {manga_obj.title}', 'green')

        for genre in genres:
            if genre not in manga_obj.genre:
                manga_obj.genre.append(genre)
                pprint(f'[!] Info: Genre {genre.slug} added to {manga_obj.title}', 'green')

        chapters = self.idx_chapter(manga['chapters'], {'manga':manga_obj})

        # will send a notification to every person that has this manga on his favorites
        if type(chapters) is list:
            users_that_favorited = Favorites.query.filter_by(manga_id=manga_obj.id).all()
            for user in users_that_favorited:
                title = f'New chapters on {manga_obj.title}' if len(chapters) == 1 else f'New chapter on {manga_obj.title}'
                ch_titles = [ch.title for ch in chapters]
                message = f'There are {len(chapters)} new chapters on {manga_obj.title} - {", ".join(ch_titles)}'

                Notifications.send_notification(user.user_id, title, message)
                pprint(f'[i] Info: Notification sent to {user.username}.', 'green')
            db.session.commit()

        return manga_obj

    def idx_source(self, source: str, source_lang: str, source_url: str):
        source_obj = Sources.query.filter_by(slug=source).first()

        if not source_obj:
            source_obj = Sources(
                slug=source,
                title=source.title(),
                lang=source_lang,
                url=source_url
            )
            db.session.add(source_obj)
            db.session.commit()

            source_obj = Sources.query.filter_by(slug=source).first()
            pprint(f'[i] Info: Source {source_obj.slug} created.', 'green')

        return source_obj

    def idx_status(self, status: str):
        status_obj = Status.query.filter_by(slug=status).first()

        if not status_obj:
            status_obj = Status(
                slug=status
            )
            db.session.add(status_obj)
            db.session.commit()

            status_obj = Status.query.filter_by(slug=status).first()
            pprint(f'[i] Info: Status {status_obj.slug} created.', 'green')

        return status_obj

    def idx_author(self, author: str):
        author_obj = Authors.query.filter_by(slug=author).first()

        if not author_obj:
            author_obj = Authors(
                slug=author
            )
            db.session.add(author_obj)
            db.session.commit()

            author_obj = Authors.query.filter_by(slug=author).first()
            pprint(f'[i] Info: Author {author_obj.slug} created.', 'green')

        return author_obj

    def idx_genre(self, genre: str):
        genre_obj = Genres.query.filter_by(slug=genre).first()

        if not genre_obj:
            genre_obj = Genres(
                slug=genre
            )
            db.session.add(genre_obj)
            db.session.commit()

            genre_obj = Genres.query.filter_by(slug=genre).first()
            pprint(f'[i] Info: Genre {genre_obj.slug} created.', 'green')

        return genre_obj

    def idx_manga_title(self, manga: dict, complements: dict):
        manga_obj = Mangas.query.filter_by(slug=manga['slug'], source=complements['source'].id).first()

        if not manga_obj:
            manga_obj = Mangas(
                slug = manga['slug'],
                title = manga['title'],
                image = manga['image'],
                status = complements['status'].id,
                views = manga['views'],
                description = manga['description'],
                source = complements['source'].id,
            )
            db.session.add(manga_obj)
            db.session.commit()

            manga_obj = Mangas.query.filter_by(slug=manga['slug'], source=complements['source'].id).first()
            pprint(f'[i] Info: Manga status {manga_obj.title} is {complements["status"].slug}.', 'green')
            pprint(f'[i] Info: Manga {manga_obj.title} indexed.', 'green')

        else:
            manga_obj.image = manga['image']
            db.session.commit()
            pprint(f'[i] Info: Manga {manga_obj.title} already indexed.', 'yellow')

        return manga_obj

    def idx_tool_find_chapter(self, chapters: dict, complements: dict):
        # will do a routine of checking what chapter was the last indexed
        last_chapter = Chapters.query.filter_by(slug=chapters[0]['slug'], manga_id=complements['manga'].id).first()
        if last_chapter is None:
            step_through_chapters = round(len(chapters)/7) * -1 if round(len(chapters)/7) != 0 else -1

            for chapter in chapters[::step_through_chapters]:
                chapter_obj = Chapters.query.filter_by(slug=chapter['slug'], manga_id=complements['manga'].id).first()

                if not chapter_obj:
                    return chapters.index(chapter) - step_through_chapters

            else:
                return step_through_chapters

        else:
            pprint(f'[i] Info: Last chapter of {complements["manga"].title} indexed. Skipping routine.', 'yellow')

    def idx_chapter(self, chapters: dict, complements: dict):
        # will do a routine of checking what chapter was the last indexed
        last_indexed = self.idx_tool_find_chapter(chapters, complements)

        chapters_indexed = []
        if last_indexed:
            for chapter in chapters[last_indexed::-1]:
                chapter_obj = Chapters.query.filter_by(slug=chapter['slug'], manga_id=complements['manga'].id).first()
                if not chapter_obj:
                    chapter_obj = Chapters(
                        slug = chapter['slug'],
                        title = chapter['title'],
                        link = chapter['chapter_link'],
                        manga_id = complements['manga'].id,
                        updated_on_source= chapter['updated'],
                    )
                    db.session.add(chapter_obj)
                    chapters_indexed.append(chapter_obj)
                    pprint(f'[i] Info: Chapter {chapter_obj.title} of {complements["manga"].title} created.', 'green')

                else:
                    pprint(f'[i] Info: Chapter {chapter_obj.title} of {complements["manga"].title} already indexed.', 'yellow')

                db.session.commit()

            return chapters_indexed

if __name__ == '__main__':
    pass