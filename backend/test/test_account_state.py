import requests 
import proxmox_api.config.configuration as config
from .conftest import init_database
import pytest

backendURL = "http://localhost:8080/api/1.0.0";


@pytest.fixture
def client():
    init_database()

def test_valid_account_state():
    """Test case for account_state

    get all user's vms  # noqa: E501
    """
    r = requests.get(backendURL + "/account_state/valid-user", headers={'Authorization': 'Bearer AT-fake-admin-token', "fake-user": "valid-user"})
    assert r.status_code == 200
    assert r.json()['freezeState'] == '0'


def test_unknown_account_state():
    """Test case for account_state

    Even if the user is not known, the result must be 200 and 0 because its a new member, wihtout vm.
    """
    r = requests.get(backendURL + "/account_state/which-user", headers={'Authorization': 'Bearer AT-fake-admin-token', "fake-user": "which-user"})
    assert r.status_code == 200
    assert r.json()['freezeState'] == '0'


def test_expired_account_freezed_1():
    """Test case for account_state

    freeze state of 1
    """
    r = requests.get(backendURL + "/account_state/expired_user_1", headers={'Authorization': 'Bearer AT-fake-admin-token', "fake-user": "expired_user_1"})
    assert r.status_code == 200
    assert r.json()['freezeState'] == '1'

def test_expired_account_freezed_2():
    """Test case for account_state

    freeze state of 2
    """
    r = requests.get(backendURL + "/account_state/expired_user_2", headers={'Authorization': 'Bearer AT-fake-admin-token', "fake-user": "expired_user_2"})
    assert r.status_code == 200
    assert r.json()['freezeState'] == '2'

def test_expired_account_freezed_3():
    """Test case for account_state

    freeze state of 3
    """
    r = requests.get(backendURL + "/account_state/expired_user_3", headers={'Authorization': "Bearer AT-fake-admin-token", "fake-user": "expired_user_3"})
    assert r.status_code == 200
    assert r.json()['freezeState'] == '3'

def test_expired_account_freezed_4():
    """Test case for account_state

    freeze state of 4
    """
    r = requests.get(backendURL + "/account_state/expired_user_4", headers={'Authorization': 'Bearer AT-fake-admin-token', "fake-user": "expired_user_4"})
    assert r.status_code == 200
    assert r.json()['freezeState'] == '4'


def test_new_account_to_be_checked():
    """Test case for account_state

    Account that must be checked by adh6
    """
    r = requests.get(backendURL + "/account_state/new-user-to-be-checked", headers={'Authorization': 'Bearer AT-fake-admin-token', "fake-user": "new-user-to-be-checked"})
    assert r.status_code == 200
    assert r.json()['freezeState'] == '0'