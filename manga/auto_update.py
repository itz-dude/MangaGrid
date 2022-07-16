# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys

sys.path.append(os.getcwd())

import concurrent.futures
import time

from extensions import sources
from tools import clear


# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

def refresh_routine():
    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for obj in sources:
                executor.submit(sources[obj]['object']().refresh_routine)

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