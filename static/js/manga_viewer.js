class MangaViewer {
    constructor() {
        this.url_args = this.urlArgs();
        
        this.initialBehavior();
        this.searching();
    }

    initialBehavior() {
        if (!this.url_args.hasOwnProperty('id') || !this.url_args.hasOwnProperty('source')) {
            modals.errorMsg('No parameters inserted.');
        }
    }

    async searching () {
        this.manga = await this.searchManga(this.url_args.source, this.url_args.id);
        if (this.manga.hasOwnProperty('error')) {
            modals.errorMsg(this.manga.error);
        } else {
            this.renderManga(this.manga);
        }
    }

    renderManga (manga) {
        $('.while-loading').toggleClass('while-loading');

        $('#mangaSource').text(this.capitalize(manga.source));
        $('#mangaImage').attr('src', manga.image);
        $('#mangaTitle').text(manga.title);

        $('#mangaAuthors').text(manga.author.join(', '));
        $('#mangaStatus').text(manga.status);
        $('#mangaGenres').text(manga.genres.join(', '));
        $('#mangaUpdated').text(manga.updated);
        $('#mangaViews').text(manga.views);

        $('#mangaDescription').text(manga.description);

        $('.chapter-no').remove();

        manga.chapters.forEach(ch => {
            $(
            `<li class="chapter-no">
                <a href="${ch.chapter_link}" class="">${ch.title}.</a>
                <div class="last-updated">${ch.updated}.</div>
            </li>`
            ).appendTo('.chapter-list');
        });
    }

    // tools

    urlArgs () {
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        var args = {};
        for (var i = 0; i < vars.length; i++) {
            var pair = vars[i].split("=");
            args[pair[0]] = pair[1];
        }
        return args;
    }

    async searchManga (source, target) {
        let url = `/api/manga/${source}/${target}`
        let response = await fetch(url)
        let result = await response.json()
        return result
    }

    capitalize(word) {
        return word[0].toUpperCase() + word.slice(1).toLowerCase();
    }
}

new MangaViewer();