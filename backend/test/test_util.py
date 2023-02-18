import pytest
from proxmox_api import util



# Test to subscribe hosting_api real adh6 account to the ML.
def test_subscribe_to_hosting_ML():
    _,status = util.subscribe_to_hosting_ML("hosting_api")
    assert status == 204

