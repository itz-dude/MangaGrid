sources = [
    'manganato',
    'mangalife',
    'mangahere'
]

def c_response (status=200, message=None, data=None):
    return {
        'status': status,
        'message': message,
        'data': data
    }