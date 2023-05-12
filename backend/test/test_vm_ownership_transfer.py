import pytest
from test.conftest import *
from proxmox_api import proxmox
from proxmox_api import util
from proxmox_api.db import db_functions as database


def fake_get_adh6_account(newowner):
    return {"username": newowner}, 200


# Transfer a vm to another user, who exists in hosting and has less than 3 vms
def test_vm_ownership_transfer(monkeypatch, init_user_database, init_vm_database):
    username = "user-2"
    monkeypatch.setattr(util, "get_adh6_account", fake_get_adh6_account)
    vmid = 1
    body, status = proxmox.transfer_ownership(vmid, username)

    # return status
    assert status == 201
    assert body == {"status": "ok"}

    # Check that the vm is now owned by user-2
    userid = database.get_vm_userid(vmid)
    assert userid == username

    # Check that the history is updated
    history = database.get_historyip_fromdb(vmid)
    assert history[-1][2] == username


# Transfer a vm to another user, who doesn't exist in hosting but exist in adh6
def test_vm_ownership_transfer_to_new_user(
    monkeypatch, init_user_database, init_vm_database
):
    username = "new-user"
    monkeypatch.setattr(util, "get_adh6_account", fake_get_adh6_account)
    vmid = 1
    body, status = proxmox.transfer_ownership(vmid, username)

    # return status
    assert status == 201
    assert body == {"status": "ok"}

    # Check that the user is created in the database
    assert database.get_user_list(user_id=username) is not None

    # Check that the vm is now owned by user-2
    userid = database.get_vm_userid(vmid)
    assert userid == username

    # Check that the history is updated
    history = database.get_historyip_fromdb(vmid)
    assert history[-1][2] == username


# Transfer a vm to another user, who doesn't exist in hosting not in adh6
def test_vm_ownership_to_nonexistent_user(
    monkeypatch, init_user_database, init_vm_database
):
    username = "nonexistent-user"

    def fake_get_adh6_account_None(newowner):
        return None, 200

    monkeypatch.setattr(util, "get_adh6_account", fake_get_adh6_account_None)
    vmid = 1
    body, status = proxmox.transfer_ownership(vmid, username)

    # return status
    assert status == 404
    assert body == {"error": "User not found"}


# Transfer a vm to another user, who has already 3 vms
def test_vm_ownership_to_full_user(monkeypatch, init_user_database, init_vm_database):
    username = "user-1"  # User-1 has 3 vms
    monkeypatch.setattr(util, "get_adh6_account", fake_get_adh6_account)
    vmid = 3  # vmid 3 is owned by user-2
    body, status = proxmox.transfer_ownership(vmid, username)

    # return status
    assert status == 400
    assert body == {"error": "User already has 3 VMs"}

    # We check that the vm is still owned by user-2
    # Check that the vm is now owned by user-2
    userid = database.get_vm_userid(vmid)
    assert userid == "user-2"
