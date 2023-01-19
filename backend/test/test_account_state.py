import requests 
import proxmox_api.config.configuration as config
import pytest
import requests
import proxmox_api
import proxmox_api.controllers.default_controller as controller
from proxmox_api import util
import proxmox_api.proxmox as proxmox
import proxmox_api.__main__ as main
from proxmox_api.config.configuration import *
import proxmox_api.db.db_models as db_models
from flask_sqlalchemy import SQLAlchemy
from test.conftest import *

#backendURL = "http://localhost:8080/api/1.0.0";


#@pytest.fixture
#def client():
#    init_user_database()

def test_valid_account_state(monkeypatch, init_user_database):
    """Test case for account_state

    get all user's vms  # noqa: E501
    """
    #mocker.patch('proxmox_api.util.check_cas_token', return_value= (200, {'sub': "valid-user"}))
    #monkeypatch.setattr(util, 'check_cas_token', (200,{'sub': "valid-user"}))

    #r = requests.get(backendURL + "/account_state/valid-user", headers={'Authorization': 'Bearer AT-fake-admin-token', "fake-user": "valid-user"})
    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        r = proxmox.get_freeze_state("valid-user")
        dict,status_code = r
        assert status_code == 200
        assert dict['freezeState'] == '0'


def test_unknown_account_state(mocker, init_user_database):
    """Test case for account_state

    Even if the user is not known, the result must be 200 and 0 because its a new member, wihtout vm.
    """

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        r = proxmox.get_freeze_state("unknown-user")
        dict,status_code = r
        assert status_code == 200
        assert dict['freezeState'] == '0'


def test_expired_account_freezed_1(monkeypatch, init_user_database):
    """Test case for account_state

    freeze state of 1
    """
    username = "expired-user-1"
    def fake_get_adh6_account(username):
        return {'username' : username},200


    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        monkeypatch.setattr(util, 'get_adh6_account', fake_get_adh6_account)
        r = proxmox.get_freeze_state(username)
        dict,status_code = r
        assert status_code == 200
        assert dict['freezeState'] == '1'

def test_expired_account_freezed_2(monkeypatch, init_user_database):
    """Test case for account_state

    freeze state of 2
    """

    username = "expired-user-2"
    def fake_get_adh6_account(username):
        return {"username":username},200

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        monkeypatch.setattr(util, 'get_adh6_account', fake_get_adh6_account)
        r = proxmox.get_freeze_state(username)
        dict,status_code = r
        assert status_code == 200
        assert dict['freezeState'] == '2'

def test_expired_account_freezed_3(monkeypatch, init_user_database):
    """Test case for account_state

    freeze state of 3
    """

    username = "expired-user-3"
    def fake_get_adh6_account(username):
        return {'username' : username},200

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        monkeypatch.setattr(util, 'get_adh6_account', fake_get_adh6_account)

        r = proxmox.get_freeze_state(username)
        dict,status_code = r
        assert status_code == 200
        assert dict['freezeState'] == '3'

def test_expired_account_freezed_4(monkeypatch,init_user_database):
    """Test case for account_state

    freeze state of 4
    """

    username = "expired-user-4"
    def fake_get_adh6_account(username):
        return {'username' : username}, 200

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        monkeypatch.setattr(util, 'get_adh6_account', fake_get_adh6_account)
        r = proxmox.get_freeze_state(username)
        dict,status_code = r
        assert status_code == 200 
        assert dict['freezeState'] == '4'


def test_new_account_to_be_checked(monkeypatch, init_user_database):
    """Test case for account_state

    Account that must be checked by adh6
    """

    username = "new-user-to-be-checked"
    def fake_get_adh6_account(username):
        return {'ip': "127.0.0.1", "departureDate" : "2199-01-01", 'username' : username}, 200

    
    
    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        monkeypatch.setattr(util, 'get_adh6_account', fake_get_adh6_account)
        r = proxmox.get_freeze_state(username)
        dict,status_code = r
        assert status_code == 200
        assert dict['freezeState'] == '0'