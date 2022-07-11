class SearchSource {
    constructor (source) {
        this.source = $(`#${source}`)
        this.target = $('#searchNameTarget').text()
        this.container = this.source.find('.source-content')

        this.initialization()
    }

    async initialization () {
        this.source.find('.source-header').toggleClass('searching')

        let results = await this.search()
        let keys = Object.keys(results)

        if (keys[0] == 'error') {
            this.source.find('.source-header').toggleClass('searching')
            this.source.find('.source-header').toggleClass('error')
        } else if (keys.length > 0) {
            this.source.find('.source-header').toggleClass('searching')

            let style = {
                height: '23em',
                'padding-top': '1em',
                'padding-bottom': '1em',
            }
            this.container.animate(style, 500, () => {
                $(this).css(style)
            })

            let index = 0
            keys.forEach(key => {
                let card = this.renderCard(
                    `${key}`,
                    results[`${key}`].author,
                    results[`${key}`].chapter,
                    results[`${key}`].image,
                    results[`${key}`].link,
                    results[`${key}`].link_chapter,
                    results[`${key}`].updated,
                )
                
                this.container.append(card)
                $(`#card${index}`).css({opacity: 0})
                $(`#card${index}`).animate({
                    opacity: 1
                }, 1000, () => {$(`#card${index}`).css({opacity: 1})})
            })
        } else {
            this.source.find('.source-header').toggleClass('error')
        }

    }

    async search () {
        let url = `/api/search/${this.source.attr('id')}/${this.target}`
        let response = await fetch(url)
        let result = await response.json()
        return result
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

$(document).ready(() => {
    let sources = [
        'manganato',
        'mangalife'
    ]

    sources.forEach(source => {
        if ($(`#${source}`)) {
            new SearchSource(source)
        }
    })
    
});