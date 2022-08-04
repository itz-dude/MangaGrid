from manga.modules.mangadex import Mangadex
from manga.modules.manganato import Manganato
from manga.modules.mangaschan import Mangaschan
from manga.modules.kissmanga import Kissmanga
from manga.modules.mangalife import Mangalife
from manga.modules.mangatoo import Mangatoo
from manga.modules.mangavibe import Mangavibe
from manga.modules.mangahere import Mangahere
from manga.modules.mangadex import Mangadex

sources = {
    'mangaschan' : {'language': 'pt_BR', 'object': Mangaschan},
    'mangadex' : {'language': 'en_US', 'object': Mangadex},
    'kissmanga' : {'language': 'en_US', 'object': Kissmanga},
    'mangavibe' : {'language': 'pt_BR', 'object': Mangavibe},
}