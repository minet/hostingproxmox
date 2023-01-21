import pytest
import proxmox_api.config.configuration as config
import proxmox_api.db.db_functions as database
import proxmox_api.db.db_models as model
from flask_sqlalchemy import SQLAlchemy
from proxmox_api import util
import proxmox_api.config.configuration as configuration
from proxmoxer import ProxmoxAPI
from proxmox_api.__main__ import app as flask_app

#@pytest.fixture
#def client():
#    os.environ.update({"ENVIRONNMENT": "TEST"})
#
#
@pytest.fixture()
def init_user_database():
    if configuration.ENV != "TEST":
        raise Exception("You must set the environnement to TEST to run the tests")
    db = SQLAlchemy()
    db.init_app(flask_app.app)
    with flask_app.app.app_context():
        # Create the database and the database table
        #model.User.query.delete()
        db.session.query(model.User).delete()
        db.create_all()
        # List of test users
        test_users = [
            {"id": "user-1", "freezeState": "0.0",  "lastNotificationDate": None},
            {"id": "user-2", "freezeState": "0.0",  "lastNotificationDate": None},
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
        #model.User.query.delete()
        db.session.query(model.User).delete()
        db.session.query(model.Vm).delete()
        db.session.commit()


@pytest.fixture()
def init_vm_database():
    if configuration.ENV != "TEST":
        raise Exception("You must set the environnement to TEST to run the tests")
    db = SQLAlchemy()
    db.init_app(flask_app.app)
    with flask_app.app.app_context():
        try:
            db.session.query(model.Vm).delete()
        except:
            print("No VM to delete")
        db.create_all()

        # List of test VM
        test_vms = [
            {"id" : 1, "userId" : "user-1", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 2, "userId" : "user-1", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 3, "userId" : "user-2", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 4, "userId" : "user-2", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 5, "userId" : "user-1", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False}
        ]


        # Convert the list of dictionaries to a list of User    objects
        def create_user_model(user):
            return model.User(**user)
        def create_vm_model(vms):
            return model.Vm(**vms)
        
        # Create a list of objects
        mapped_vms = map(create_vm_model, test_vms)
        t_vms = list(mapped_vms)

        db.session.add_all(t_vms)

        # Commit the changes for the users
        db.session.commit()

        yield db  # this is where the testing happens!
        db.session.remove()  # looks like db.session.close() would  work as well
        # Drop the database table
        #model.User.query.delete()
        db.session.query(model.User).delete()
        db.session.query(model.Vm).delete()
        db.session.commit()


@pytest.fixture()
def init_expired_vm_database():
    if configuration.ENV != "TEST":
        raise Exception("You must set the environnement to TEST to run the tests")
    db = SQLAlchemy()
    db.init_app(flask_app.app)
    with flask_app.app.app_context():
        try:
            db.session.query(model.Vm).delete()
        except:
            print("No VM to delete")
        db.create_all()

        # List of test VM
        test_vms = [
            {"id" : 1, "userId" : "user-1", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 2, "userId" : "expired-user-1", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 3, "userId" : "expired-user-2", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 4, "userId" : "expired-user-3", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False},
            {"id" : 5, "userId" : "expired-user-2", "type":"bare", "ip" : None, "mac" : None,"needToBeRestored" : False}
        ]


        # Convert the list of dictionaries to a list of User    objects
        def create_user_model(user):
            return model.User(**user)
        def create_vm_model(vms):
            return model.Vm(**vms)
        
        # Create a list of objects
        mapped_vms = map(create_vm_model, test_vms)
        t_vms = list(mapped_vms)

        db.session.add_all(t_vms)

        # Commit the changes for the users
        db.session.commit()

        yield db  # this is where the testing happens!
        db.session.remove()  # looks like db.session.close() would  work as well
        # Drop the database table
        #model.User.query.delete()
        db.session.query(model.User).delete()
        db.session.query(model.Vm).delete()
        db.session.commit()

@pytest.fixture()
def proxmoxAPI():
    assert configuration.PROXMOX_HOST != None 
    assert configuration.PROXMOX_USER != None
    assert configuration.PROXMOX_API_KEY_NAME != None
    assert configuration.PROXMOX_API_KEY != None

    return ProxmoxAPI(host=configuration.PROXMOX_HOST, user=configuration.PROXMOX_USER
                     , token_name=configuration.PROXMOX_API_KEY_NAME
                     , token_value=configuration.PROXMOX_API_KEY, verify_ssl=False)


@pytest.fixture(scope='module')
def client():
    with flask_app.app.test_client() as c:
        yield c