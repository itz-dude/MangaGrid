from manga.modules.manganato import Manganato
from manga.modules.mangaschan import Mangaschan
from manga.modules.kissmanga import Kissmanga
from manga.modules.mangalife import Mangalife 
from manga.modules.mangavibe import Mangavibe
from manga.modules.mangahere import Mangahere

sources = {
    'mangaschan' : {'language': 'pt_BR', 'object': Mangaschan},
    'kissmanga' : {'language': 'en_US', 'object': Kissmanga},
    # 'manganato' : {'language': 'en_US', 'object': Manganato},
    # 'mangalife' : {'language': 'en_US', 'object': Mangalife},
    # 'mangavibe' : {'language': 'pt_BR', 'object': Mangavibe},
    # 'mangahere' : {'language': 'en_US', 'object': Mangahere},
}