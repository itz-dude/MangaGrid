# ---------------- DEFAULT IMPORTS ---------------- #
# make the script return to the main directory
import os, sys

sys.path.append(os.getcwd())

import concurrent.futures
import datetime
import json
import time

from extensions import sources, db
from tools import clear, pprint

from manga.mangascrapping import MangaScrapping
from manga.models import Sources, Mangas, Authors, Genres, Chapters
from users.models import Users, History, Favorites


# -------------------- TOOLS ---------------------- #

def process_generator(func, args):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        task_1 = executor.submit(func, args)
        return task_1.result()


# ------------------- STRUCTURE ------------------- #

def refresh_routine():
    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for obj in sources:
                executor.submit(sources[obj]['object']().refresh_routine)

    except Exception as e:
        print(f'Error: {e}')

def indexing_routine():
    results = {}
    for manga in sources.keys():
        try:
            manga = f'{manga.capitalize()} ({sources[manga]["language"].split("_")[0].upper()})'
            results[manga] = {}
            with open(f'manga/results/{manga.split(" ")[0].lower()}_updates.json') as json_file:
                results[manga].update(json.load(json_file))

            for entrada in results[manga]:
                if results[manga][entrada]['updated']:
                    date = MangaScrapping().get_date_from_string(results[manga][entrada]['updated'])
                    results[manga][entrada]['updated'] = MangaScrapping().get_string_from_timestamp(date)
        
        except:
            pprint(f'[!] ERROR: / - Archive not found for {manga}', 'red')

    targets = []
    for source in results:
        for manga in results[source]:
            targets.append([results[source][manga]['source'], results[source][manga]['ref']])

    for target in targets:
        try:
            manga = Mangas.query.filter_by(slug=target[1]).first()
            pprint(f'[i] Info: Manga {manga.title} already indexed.', 'green')

        except:
            manga = sources[target[0]]['object']().access_manga(target[1])

            for genre in manga['genres']:
                verif = Genres.query.filter_by(genre=genre).first()
                if not verif:
                    genre_obj = Genres(genre)
                    db.session.add(genre_obj)
                    db.session.commit()
                    pprint(f'[i] Info: Genre {genre} added.', 'green')

            for author in manga['author']:
                verif = Authors.query.filter_by(author=author).first()
                if not verif:
                    author_obj = Authors(author)
                    db.session.add(author_obj)
                    db.session.commit()
                    pprint(f'[i] Info: Author {author} added.', 'green')

            upd_manga = Mangas.query.filter_by(slug=target[1]).first()
            if not upd_manga:
                upd_manga = Mangas(
                    title = manga['title'],
                    slug = target[1],
                    image = manga['image'],
                    status = manga['status'],
                    updated = MangaScrapping().get_timestamp_from_string(manga['updated']),
                    views = manga['views'],
                    description = manga['description'],
                    source = manga['source'],
                )
                db.session.add(upd_manga)
                db.session.commit()
                pprint(f'[i] Info: Manga {manga["title"]} added.', 'green')

                upd_manga = Mangas.query.filter_by(slug=target[1]).first()

                for genre in manga['genres']:
                    genre_obj = Genres.query.filter_by(genre=genre).first()

                    if genre_obj not in upd_manga.genre:
                        upd_manga.genre.append(genre_obj)
                        db.session.commit()
                        pprint(f'[i] Info: Genre {genre} added to {manga["title"]}.', 'green')

                for author in manga['author']:
                    author_obj = Authors.query.filter_by(author=author).first()

                    if author_obj not in upd_manga.author:
                        upd_manga.author.append(author_obj)
                        db.session.commit()
                        pprint(f'[i] Info: Author {author} added to {manga["title"]}.', 'green')

            for chapter in manga['chapters']:
                chapter_obj = Chapters.query.filter_by(slug=chapter['slug']).first()

                if chapter_obj is None:
                    chapter_obj = Chapters(
                        title = chapter['title'],
                        slug = chapter['slug'],
                        chapter_link = chapter['chapter_link'],
                        updated = MangaScrapping().get_timestamp_from_string(chapter['updated']) if chapter['updated'] in chapter else datetime.datetime.now(),
                    )
                    db.session.add(chapter_obj)
                    db.session.commit()

                if chapter_obj not in upd_manga.chapters:
                    chapter_obj.manga.append(upd_manga)
                    db.session.commit()
                    pprint(f'[i] Info: chapter {chapter["title"]} added to {manga["title"]}.', 'green')



if __name__ == '__main__':

    allow = True

    interval = 60 * 30
    interval_remaining = 0

    while allow:
        clear()
        pprint(f'[i] Current time to auto update: {interval}s.')
        pprint(f'[+] Refreshing in {interval_remaining}s.', 'green')

        if interval_remaining == 0:
            clear()
            pprint('[i] Initialiazing refreshing sources...\n', 'yellow')
            refresh_routine()
            pprint('[!] Refresh doned.\n', 'green')
            pprint('[i] Initialiazing indexing titles...\n\n', 'yellow')
            time.sleep(5)
            indexing_routine()
            pprint('\n[!] Refresh doned.\n[.] Restarting routine...', 'green')
            time.sleep(5)
            interval_remaining = interval

        time.sleep(1)
        interval_remaining -= 1