import os
from termcolor import colored

from extensions import DEBUG

# ------------------------------------------------- #

def c_response (status=200, message=None, data=None):
    return {
        'status': status,
        'message': message,
        'data': data
    }

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# hijack the print function to colorize it
def pprint(text, color = None):
    if DEBUG:
        if color is None: print(text)
        else: print(colored(text, color))


if __name__ == '__main__':
    pprint('[i] Initialiazing refreshing sources...\n', 'yellow')