# -------------- ALLOW SELF EXECUTE --------------- #
import os, sys
sys.path.append(os.getcwd())


# ------------------ IMPORTING -------------------- #
import sqlite3


# --------------------- TOOL ---------------------- #
class Database():
    def __init__(self):
        self.database = 'persistent/db.sqlite3'
        self.result = 0

    def sql_cmd(self, string, return_info = False):
        self.login = sqlite3.connect(self.database)
        cursor = self.login.cursor()
        
        try:
            print(f'COMMND: {string}')
            cursor.execute(string)
            print(f'SUCCES: {string.split()[0]} has been doned')

            if string.split()[0].lower() == 'select' \
            or 'return' in string.split():
                if return_info:
                    return cursor.fetchall()
                else:
                    print(cursor.fetchall())

            self.login.commit()

        except Exception as e:
            print(f'ERROR: {string.split()[0]} has encountered a error: {e}')

    def close(self):
        self.login.close()


if __name__ == '__main__':
    db = Database()

    db.sql_cmd('SELECT * FROM users')

    # db.sql_cmd('DROP TABLE alembic_version')

    db.close()