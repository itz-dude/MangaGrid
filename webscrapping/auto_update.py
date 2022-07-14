# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys
sys.path.append(os.getcwd())

import threading
import time

from webscrapping.modules.manganato import Manganato
from webscrapping.modules.mangahere import Mangahere
from webscrapping.modules.mangalife import Mangalife



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

def refresh_routine():
    objects = [
        Manganato, 
        Mangahere, 
        Mangalife
    ]

    try:
        for obj in objects:
            threading.Thread(target=obj().refresh_routine).start()
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':

    allow = True
    interval = 60 * 10

    while allow:
        refresh_routine()
        time.sleep(interval)