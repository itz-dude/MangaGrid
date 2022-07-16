# ------------------ IMPORTING -------------------- #

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from api.models import *
from manga.models import *
from users.models import *

from extensions import return_flask_app, db


# ----------------- SETTING APP ------------------- #

app = return_flask_app()

# iniciar migração vazia
# db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()