import os
import re
from termcolor import colored

DEBUG = True

from extensions import db

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

def check_email(email):
    if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return True
    else:
        return False

def check_password(password):
    # this funcion will check if the password have one uppercase, one lowercase, one number.
    # and if the length is bigger than 8
    if len(password) > 8:
        if re.search(r'[A-Z]', password):
            if re.search(r'[a-z]', password):
                if re.search(r'[0-9]', password):
                    return True
    return False


# ------------------------------------------------- #

class BehaviorStructure():
    # every behavior must have a self.object = Object,
    # self.every_field = [self.with, self.every, self.field]
    # and self.primary_identifier = [self.object.id==self.id]

    # -- General Behavior -- #
    def create(self):
        if self.check_all_fields() and self.read() is None:
            object_created = self.object(*self.every_field)
            db.session.add(object_created)
            db.session.commit()
            return object_created

        elif not self.check_all_fields():
            raise Exception(f'Missing field in order to create a object {self.object.__name__}')

        else:
            raise Exception(f'{self.object.__name__} already exists')

    def read(self):
        return self.object.query.filter(*self.primary_identifier).first()

    def update(self):
        ...
        # must be implemented in the child class

    def delete(self):
        object_query = self.read()

        if object_query is not None:
            db.session.delete(object_query)
            db.session.commit()
            return object_query

        else:
            raise Exception(f'{self.object.__name__} does not exist')


    # -- Checks -- #
    def check_all_fields(self):
        if self.every_field is None:
            return False

        for field in self.every_field:
            if field is None:
                return False
        
        return True


if __name__ == '__main__':
    pprint('[i] Initialiazing refreshing sources...\n', 'yellow')