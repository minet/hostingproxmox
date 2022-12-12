import pytest
import proxmox_api.config.configuration as config
import os
import proxmox_api.db.db_functions as db
from proxmox_api.db.db_models import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy




@pytest.fixture
def client():
    os.environ.update({"ENVIRONNMENT": "dev"})


@pytest.fixture()
def init_database():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    db = SQLAlchemy(app)
    # Create the database and the database table
    db.create_all()

    # List of test users
    test_users = [
        {"id": "valid-user", "freezeState": "0.0", "lastNotificationDate": None},
         {"id": "new-user", "freezeState": None, "lastNotificationDate": None},
        {"id": "expired-user", "freezeState": "1.0", "lastNotificationDate": "14/11/2022"},
    ]

    # Convert the list of dictionaries to a list of User objects
    def create_post_model(user):
        return User(**user)

    # Create a list of User objects
    mapped_users = map(create_post_model, test_users)
    t_users = list(mapped_users)

    # Add the users to the database - add_all() is used to add multiple records
    db.session.add_all(t_users)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!
    db.session.remove()  # looks like db.session.close() would work as well
    # Drop the database table
    db.drop_all()


