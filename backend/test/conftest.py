import pytest
import proxmox_api.config.configuration as config
import proxmox_api.db.db_functions as database
import proxmox_api.db.db_models as model
from flask_sqlalchemy import SQLAlchemy
from proxmox_api import util


#@pytest.fixture
#def client():
#    os.environ.update({"ENVIRONNMENT": "dev"})
#
#
@pytest.fixture()
def init_database():
    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        # Create the database and the database table
        db.create_all()

        # List of test users
        test_users = [
            {"id": "valid-user", "freezeState": "0.0",  "lastNotificationDate": None},
             {"id": "expired-user-1", "freezeState": "1.0",    "lastNotificationDate": None},
            {"id": "expired-user-2", "freezeState": "2.0",    "lastNotificationDate": None},
            {"id": "expired-user-3", "freezeState": "3.0",    "lastNotificationDate": None},
            {"id": "expired-user-4", "freezeState": "4.0",    "lastNotificationDate": None},
            {"id": "new-user-to-be-checked", "freezeState": None,    "lastNotificationDate": None},
        ]

        # Convert the list of dictionaries to a list of User    objects
        def create_post_model(user):
            return model.User(**user)

        # Create a list of User objects
        mapped_users = map(create_post_model, test_users)
        t_users = list(mapped_users)

        # Add the users to the database - add_all() is used #to dd  multiple records
        db.session.add_all(t_users)

        # Commit the changes for the users
        db.session.commit()

        yield db  # this is where the testing happens!
        db.session.remove()  # looks like db.session.close() would  work as well
        # Drop the database table
        db.drop_all()


