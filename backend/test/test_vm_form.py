import requests 
import proxmox_api.config.configuration as config
from .conftest import init_database
import pytest

backendURL = "http://localhost:8080/api/1.0.0";


#@pytest.fixture
##def client():
#    init_database()

def test_valid_account_state():
    """Test case for get_vm

    get all user's vms  # noqa: E501
    """
    r = requests.get(backendURL + "/account_state/valid-user", headers={"Authorization": "admin"})
    assert r.status_code == 200
