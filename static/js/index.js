class Header {
    constructor() {
        this.menuButton = $('#menuMobile');
        this.menuStatus = false;

        this.initialBehavior();
    }

    initialBehavior() {
        this.menuButton.click(() => {
            this.toggleMenu();
        });

        $('#headOptionProfile').click(() => {
            this.triggerLogin();
        });
    }

    toggleMenu() {
        if (this.menuStatus) {
            $('#menuOptions').toggleClass('menu-mobile-active');
            this.menuButton.css({'transform': 'rotate(0deg)'});
            this.menuStatus = false;
        } else {
            $('#menuOptions').toggleClass('menu-mobile-active');
            this.menuButton.css({'transform': 'rotate(180deg)'});
            this.menuStatus = true;
        }
    }

    async triggerLogin() {
        let url = '/api/users/session/is_alive';
        let response = await fetch(url)
        let result = await response.json()
        if (result.status == 200) {
            window.location.href = `/profile`;
        } else {
            window.location.href = `/login`;
        }
    }
}

class Modals {
    constructor() {
        this.initialBehavior();
    }

    initialBehavior() {
        this.newOptions = {
            "headOptionManga": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "headOptionAbout": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "headOptionContact": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "footOptionPrivacy": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "footOptionTerms": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "footOptionAbout": [
                "Website in development",
                "By: <br> <a class='icon icon-github' href='https://github.com/grigio888'>Vinicius Grigio</a><a class='icon icon-github' href='https://github.com/phzsantos'>Paulo Henrique</a>"
            ],
        }

        Object.keys(this.newOptions).forEach(key => {
            $(`#${key}`).click(() => {
                this.enteringModal(`${key}Modal`, this.newOptions[key][0], this.newOptions[key][1]);

                // closing modal
                $(`.modal-close`).click(() => {
                    this.exitingModal(`.modal-background`);
                });
            });
        });
    }

    enteringModal(id, title, content) {
        $('<div>').addClass('modal-background').appendTo('body');
        $('<div>').addClass('modal').attr('id', id).appendTo('.modal-background');
        
        $('<span></span>').addClass('icon').addClass('modal-close').appendTo('.modal');
        $('<div>').addClass('modal-content').appendTo('.modal');

        $('<div>').addClass('modal-header').appendTo('.modal-content');
        $(`<h2>${title}</h2>`).appendTo('.modal-header');

        $('<div>').addClass('modal-body').appendTo('.modal-content');
        $(`<p>${content}</p>`).appendTo('.modal-body');

        $('.modal-background').css({'opacity': 0});
        $('.modal-background').animate({
            opacity: 1
        }, 250);
    }

    exitingModal(tag) {
        $(tag).animate({
            opacity: 0
        }, 250, () => {
            $(`${tag}`).remove();
        });
    }

    errorMsg (msg) {
        this.enteringModal(
            `errorModal`,
            'Error',
            `Looks like we entered on a dead end.<br>I'll send you back.<br><br>${msg}`);
        setTimeout(() => {
            window.location.href = `/`;
        }, 2000);
    }

    alertMsg (msg) {
        this.enteringModal(
            `alertModal`,
            'Oops',
            `${msg}`
        );
        $(`.modal-close`).click(() => {
            this.exitingModal(`.modal-background`);
        }); 
    }
}

class SearchBar {
    constructor() {
        this.searchInput = $('#searchInput');
        this.searchButton = $('#searchButton');

        this.initialBehavior();
    }

    initialBehavior() {
        this.searchButton.click((e) => {
            this.search(e);
        });
    }

    search(e) {
        e.preventDefault();

        if (this.searchInput.val().length > 0) {
            window.location.href = `/search?source=all&target=${this.searchInput.val()}`;
        } else {
            modals.enteringModal(`searchModal`, 'Oops', 'Looks like you forgot to type something.');

            // closing modal
            $(`.modal-close`).click(() => {
                modals.exitingModal(`.modal-background`);
            });
        }
    }
}

class MangaViewer {
    constructor() {
        this.url_args = this.urlArgs();
        
        // searching if the string 'manga_viewer' is in the document.location.href
        if (document.location.href.indexOf('manga_viewer') > -1) {
            this.initialBehavior();
            this.searching();
        }
    }

    initialBehavior() {
        if (!this.url_args.hasOwnProperty('id') ||  this.url_args.id == '') {
            modals.errorMsg('No ID inserted.');
        } else if (!this.url_args.hasOwnProperty('source') || this.url_args.source == '') {
            modals.errorMsg('No source inserted.');
        }
    }

    async searching () {
        this.manga = await this.searchManga(this.url_args.source, this.url_args.id);
        if (this.manga.status == 404) {
            modals.errorMsg(this.manga.message);
        } else if (this.manga.status == 500 && !this.url_args.hasOwnProperty('error')) {
            modals.alertMsg(`An error ocourred on the server. Maybe it's busy.<br>I'll refresh the page.<br><br>${this.manga.message}`);
            setTimeout(() => {
                window.location.href = `/manga_viewer?source=${this.url_args.source}&id=${this.url_args.id}&error=true`;
            }, 2000);
        } else if (this.manga.status == 500 && this.url_args.hasOwnProperty('error') && this.url_args.error == 'true') {
            modals.errorMsg(`${this.manga.message}`);
        } else {
            this.renderManga(this.manga.data);
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
        let url = `/api/manga/view/${source}/${target}`
        let response = await fetch(url)
        let result = await response.json()
        return result
    }

    capitalize(word) {
        return word[0].toUpperCase() + word.slice(1).toLowerCase();
    }
}

class SearchSource {
    constructor () {
        this.sources = ['manganato','mangavibe', 'mangalife','mangahere']

        if (document.location.href.indexOf('search') > -1) {
            this.initialization()
        }
    }

    async initialization () {
        // commented by now cuz it must exhibit in the order that
        // the sources was sended by the server.
        this.sources = await fetch('/api/manga/avaliable_sources')
        this.sources = await this.sources.json()

        if (this.sources.status == 200) {
            this.sources = Object.keys(this.sources.data)
        } else {
            modals.errorMsg(this.sources.message)
        }

        let url_args = mangaViewer.urlArgs()

        if (!url_args.hasOwnProperty('source') || url_args.source == '') {
            modals.errorMsg('No source inserted.');
        } else if (url_args.source != 'all' && !this.sources.includes(url_args.source)) {
            // console.log(this.sources.includes(url_args.source))
            modals.errorMsg('Invalid source.');
        } else if (!url_args.hasOwnProperty('target') || url_args.target == '') {
            modals.errorMsg('No target inserted.');
        }

        $('#searchNameTarget').text(url_args.target.replace(/_/g, ' ').replace('%20', ' '));

        if (url_args.source == 'all') {
            this.sources.forEach(async source => {
                await this.sourceSearch(source, url_args.target);
            });
        } else {
            await this.sourceSearch(url_args.source, url_args.target);
        }
    }

    creatingSearchContainer(source) {
        $('<div>').attr('id', `${source}`).addClass('source-container').appendTo('.search')
        $('<div>').attr('id', `${source}-header`).addClass('source-header').addClass('searching').appendTo(`#${source}`)
        $('<h2>').text(`${source}`).appendTo(`#${source}-header`)
        $('<div>').addClass('source-content').appendTo(`#${source}`)
    }

    async search (source, target) {
        let url = `/api/manga/search/${source}/${target}`
        let response = await fetch(url)
        let result = await response.json()
        return result
    }

    async sourceSearch (source, target) {
        this.creatingSearchContainer(source);

        // locating elements
        let source_header = $(`#${source}-header`)
        let container = $(`#${source}`).find('.source-content')

        let results = await this.search(source, target);
        
        if (results.status == 500 || results.status == 400 || results.status == 404) {
            source_header.toggleClass('searching')
            source_header.toggleClass('error')
        } else {
            let keys = Object.keys(results.data)
            source_header.toggleClass('searching')

            container.toggleClass('active')

            let index = 0
            keys.forEach(key => {
                let card = this.renderCard(
                    `${key}`,
                    results.data[`${key}`].author,
                    results.data[`${key}`].chapter,
                    results.data[`${key}`].image,
                    results.data[`${key}`].link,
                    results.data[`${key}`].link_chapter,
                    results.data[`${key}`].updated,
                )
                
                container.append(card)
                $(`#card${index}`).css({opacity: 0})
                $(`#card${index}`).animate({
                    opacity: 1
                }, 1000, () => {$(`#card${index}`).css({opacity: 1})})
                index ++
            })
        }
    }

    renderCard (title, author, chapter, image_url, manga_link, chapter_link, updated) {
        return $(`
        <div id="${title}" class="card-result">
            <div class="card-result-image">
                <img class="card-image" src="${image_url}" alt="${title} cover">
            </div>
            <div class="card-result-info">
                <h2>
                    <a href="${manga_link}">
                        <span class="card-title">
                            ${title}
                        </span>
                    </a>
                </h2>
                <p>
                    <span class="card-link-text">
                        ${author}
                    </span>
                </p>
                <p>
                    <a class="card-link" href="${chapter_link}">
                        <span class="card-link-text">
                            ${chapter} <br> ${updated}
                        </span>
                    </a>
                </p>
            </div>
        </div>
        `)
    }
}

class Login {
    constructor () {
        if (document.location.href.indexOf('login') > -1) {
            this.initialization()
        }
    }

    initialization () {
        ['.seach-menu','#headOptionHome','#headOptionManga'].forEach(function(item) {
            $(item).hide();
        })

        $('#email').focus();
        $('#email').on('input', function() {
            if ($(this).val() != '') {
                $('#rowEmail').addClass('form-row-active')
            } else {
                $('#rowEmail').removeClass('form-row-active')
            }
        });
        $('#password').on('input', function() {
            if ($(this).val() != '') {
                $('#rowPassword').addClass('form-row-active')
            } else {
                $('#rowPassword').removeClass('form-row-active')
            }
        });

        $('#loginButton').click((e) => {
            this.loginPreValidation(e);
        });
        $('#registerButton').click((e) => {
            e.preventDefault();
            modals.alertMsg('Register not yet available.');
        });
    }

    async loginPreValidation(e) {
        e.preventDefault();

        let username = $('#email').val();
        let password = $('#password').val();

        if (username == '') {
            modals.alertMsg('No username inserted.');
        } else if (password == '') {
            modals.alertMsg('No password inserted.');
        } else {
            let resp = await this.login(username, password);
            if (resp.status == 200) {
                window.location.href = '/profile';
            } else {
                modals.alertMsg(resp.message);
            }
        }
    }

    async login (username, password) {
        let url = `/api/users/login`
        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        let result = await response.json()
        return result
    }
}

let header = new Header();
let modals = new Modals();
let searchBar = new SearchBar();
let mangaViewer = new MangaViewer();
let searchSource = new SearchSource();
let login = new Login();