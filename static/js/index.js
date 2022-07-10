class MenuMobile {
    constructor() {
        this.menuButton = $('#menuMobile');
        this.menuStatus = false;

        this.initialBehavior();
    }

    initialBehavior() {
        this.menuButton.click(() => {
            this.toggleMenu();
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
}

class Modals {
    constructor() {
        this.initialBehavior();
    }

    initialBehavior() {
        this.options = [
            "headOptionHome",
            "headOptionManga",
            "headOptionAbout",
            "headOptionContact",
            "footOptionPrivacy",
            "footOptionTerms",
            "footOptionAbout"
        ]

        this.options.forEach(option => {
            // opening modal with generic message
            $(`#${option}`).click(() => {
                console.log(option);
                this.enteringModal(`${option}Modal`, "Testing", "This is a generic message");

                // closing modal
                $(`.modalBackground`).click(() => {
                    this.exitingModal(`.modalContainer`);
                });
            });
        });
    }

    enteringModal(id, title, content) {
        let modal = $(`
        <div id="modalContainer">
            <div class="modalBackground"></div>
            <div class="modal" id="${id}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>${title}</h2>
                        <span class="close">&times;</span>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            </div>
        </div>
        `);

        $('body').append(modal);
    }

    exitingModal(id) {
        $(`#${id}`).remove();
    }
}

new MenuMobile();
new Modals();