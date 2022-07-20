# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures
import datetime

from flask import Blueprint, jsonify, session

from extensions import sources, db
from tools import c_response, pprint
from manga.mangascrapping import MangaScrapping

from manga.models import Sources, Mangas, Authors, Genres, Chapters
from users.models import Users, History

# ------------------------------------------------- #
# -------------------- TOOLS ---------------------- #
# ------------------------------------------------- #

def process_generator(func, args):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        task_1 = executor.submit(func, args)
        return task_1.result()

# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
manga = Blueprint('manga', __name__)

@manga.route('/avaliable_sources')
def avaliable_sources():
    data = {}
    for s in sources:
        data[s] = sources[s]['language']

    return jsonify(c_response(200, 'Sources avaliable', data))

@manga.route('/chapter/<string:source>/<string:search>')
def chapter(source, search):
    try:
        obj = sources[source]['object']
        task = process_generator(obj().get_chapter_content, search)

        if task:
            chapter_obj = Chapters.query.filter_by(slug=search).first()

            if chapter_obj and 'email' in session:
                user = Users.query.filter_by(email=session['email']).first()
                manga = Mangas.query.filter(Mangas.chapters.contains(chapter_obj)).first()

                if user.history.filter(History.manga_id == manga.id).first():
                    user.history.filter(History.manga_id == manga.id).first().chapter_id = chapter_obj.id
                    pprint(f'[i] Info: chapter {chapter_obj.title} added to the history {user.username}.', 'green')
                else:
                    pprint(f'[i] Info: Endpoint not resolved.', 'yellow')
                db.session.commit()

            return jsonify(c_response(200, 'Chapter fetched succesfully', task))

        else:
            pprint(f'[!] ERROR: /api/manga/chapter - Chapter not found for {search}')
            return jsonify(c_response(404, 'No results'))

    except KeyError:
        pprint(f'[!] ERROR: /api/manga/chapter - Source ({source}) not found', 'red')
        return jsonify(c_response(400, 'Source not avaliable'))

    except Exception as e:
        pprint(f'[!] ERROR: /api/manga/chapter - General exception. {e}', 'red')
        return jsonify(c_response(500, str(e)))

@manga.route('/search/<string:source>/<string:search>')
def search(source, search):
    try:
        obj = sources[source]['object']
        task = process_generator(obj().search_title, search)

        if task:
            return jsonify(c_response(200, 'Search results', task))

        else:
            pprint(f'[!] ERROR: /api/manga/search - No results for {search}')
            return jsonify(c_response(404, 'No results'))

    except KeyError:
        pprint(f'[!] ERROR: /api/manga/search - Source ({source}) not found', 'red')
        return jsonify(c_response(400, 'Source not avaliable'))

    except Exception as e:
        pprint(f'[!] ERROR: /api/manga/search - General exception. {e}', 'red')
        return jsonify(c_response(500, str(e)))

@manga.route('/view/<string:source>/<string:search>')
def view(source, search):
    try:
        manga = process_generator(sources[source]['object']().access_manga, search)

        if not manga:
            pprint(f'[!] ERROR: /api/manga/view - Manga not found for {search}')
            return jsonify(c_response(404, 'Manga not found')), 404

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

        upd_manga = Mangas.query.filter_by(slug=search).first()
        if not upd_manga:
            upd_manga = Mangas(
                title = manga['title'],
                slug = search,
                image = manga['image'],
                status = manga['status'],
                updated = MangaScrapping().get_timestamp_from_string(manga['updated']),
                views = manga['views'],
                description = manga['description'],
                source = source,
            )
            db.session.add(upd_manga)
            db.session.commit()
            pprint(f'[i] Info: Manga {manga["title"]} added.', 'green')

        upd_manga = Mangas.query.filter_by(slug=search).first()

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
                    updated = MangaScrapping().get_timestamp_from_string(chapter['updated']),
                )
                db.session.add(chapter_obj)
                db.session.commit()

            if chapter_obj not in upd_manga.chapters:
                chapter_obj.manga.append(upd_manga)
                db.session.commit()
                pprint(f'[i] Info: chapter {chapter["title"]} added to {manga["title"]}.', 'green')

        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            history = History.query.filter_by(user_id=user.id, manga_id=upd_manga.id).first()

            if not history:
                history = History(
                    user_id = user.id,
                    manga_id = upd_manga.id
                )
                db.session.add(history)
                db.session.commit()
                pprint(f'[i] Info: Added {upd_manga.title} to the history of {user.username}.', 'green')

            else:
                history.updated_at = datetime.datetime.now()
                db.session.commit()
                pprint(f'[i] Info: Updated {upd_manga.title} on the history of {user.username}.', 'green')

        else:
            pprint(f'[i] Info: User not logged in.', 'yellow')

        return jsonify(c_response(200, 'Target captured', manga))

    except KeyError as e:
        pprint(f'[!] ERROR: {e}', 'red')
        pprint(f'[!] ERROR: /api/manga/view - Source ({source}) not found', 'red')
        return jsonify(c_response(404, 'Source not found')), 404

    except Exception as e:
        pprint(f'[!] ERROR: /api/manga/view - General exception. {e}', 'red')
        return jsonify(c_response(500, 'An thread exception, not communicable.')), 500