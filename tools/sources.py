from manga.modules.goldenmangas import GoldenMangas
from manga.modules.mangadex import Mangadex
from manga.modules.mangaschan import Mangaschan
from manga.modules.kissmanga import Kissmanga
from manga.modules.mangavibe import Mangavibe
from manga.modules.mangadex import Mangadex

sources = {
    'mangaschan' : {'language': 'pt_BR', 'object': Mangaschan},
    'mangadex' : {'language': 'en_US', 'object': Mangadex},
    'kissmanga' : {'language': 'en_US', 'object': Kissmanga},
    # 'mangavibe' : {'language': 'pt_BR', 'object': Mangavibe},
    'goldenmangas' : {'language': 'pt_BR', 'object': GoldenMangas},
}