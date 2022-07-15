# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys
sys.path.append(os.getcwd())

import concurrent.futures
import threading
import time

from manga.modules.manganato import Manganato
from manga.modules.mangahere import Mangahere
from manga.modules.mangalife import Mangalife
from manga.modules.mangavibe import Mangavibe

from tools import clear


# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

def refresh_routine():
    objects = [
        Manganato().refresh_routine, 
        Mangahere().refresh_routine, 
        Mangalife().refresh_routine,
        Mangavibe().refresh_routine,
    ]

    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for obj in objects:
                executor.submit(obj)

    except Exception as e:
        print(f'Error: {e}')




if __name__ == '__main__':

    allow = True

    interval = 60
    interval_remaining = 0

    while allow:
        clear()
        print(f'[i] Current time to auto update: {interval}s.\n[+] Refreshing in {interval_remaining}s.')

        if interval_remaining == 0:
            clear()
            print('[i] Initialiazing refreshing sources...\n')
            refresh_routine()
            print('[!] Refresh finished.\n\n[.] Restarting routine...')
            time.sleep(5)
            interval_remaining = interval

        time.sleep(1)
        interval_remaining -= 1