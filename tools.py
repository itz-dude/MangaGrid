import os

# ------------------------------------------------- #

def c_response (status=200, message=None, data=None):
    return {
        'status': status,
        'message': message,
        'data': data
    }

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')