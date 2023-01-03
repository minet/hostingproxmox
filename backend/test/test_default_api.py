import pytest
import connexion
from proxmox_api import encoder
from proxmox_api import util
from test.conftest import *
from proxmox_api import proxmox
from proxmox_api.controllers import default_controller
import json


def fake_check_cas_token(headers):
    return 200, {"sub": "user-1"}
def fake_check_cas_token_fail(headers):
    return 500, {"sub": "user-1"}
def fake_check_cas_admin(headers):
    return 200, {"sub": "admin", "attributes" : {"memberOf" : 'cn=cluster-hosting,ou=groups,dc=minet,dc=net'}}
def fake_get_node_from_vm(vmid):
    return "wammu"
def fake_get_proxmox_vm_status(vmid, node):
    return "running"
def fake_get_vm_config(vmid, node):
        return  {"name": "test"},200



#####
## get_vm_id
## GET /api/1.0.0/vm/{vmid}
#####


# Valid user with valid token. Not admin.
def test_valid_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):

    

    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)

    response = client.get('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert response.status_code == 200

# Valid user with not valid token. Not admin.
def test_false_token_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):

    

    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)

    response = client.get('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert response.status_code == 403

#  valid user with a valid token. Not admin. Trying to access to another's vm.
def test_foreign_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):

    

    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)

    response = client.get('/api/1.0.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert response.status_code == 403

#  admin
def test_admin_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):

    

    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)

    vm1 = client.get('/api/1.0.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    vm2 = client.get('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert vm1.status_code == 200
    assert vm2.status_code == 200



#####
## delete_vm_id
## delete /api/1.0.0/vm/{vmid}
#####

def fake_delete_vm_in_thread(vmid, user_id, node="", dueToError=False):
    return True

# Valid user with valid token. Not admin.
def test_valid_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):    
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 200


# Valid user with not valid token. Not admin.
def test_false_token_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403

#  valid user with a valid token. Not admin. Trying to delete an another's vm.
def test_foreign_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):    
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/api/1.0.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403

#  admin
def test_admin_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    vm1 = client.delete('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    vm2 = client.delete('/api/1.0.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert vm1.status_code == 200
    assert vm2.status_code == 200


#####
## patch_vm
## patch /api/1.0.0/vm/{vmid}
#####

def fake_start_vm(vmide, node):
    return {"status": "start OK"},200

def fake_reboot_vm(vmide, node):
    return {"status": "reboot OK"},200

def fake_stop_vm(vmide, node):
    return {"status": "stop OK"},200

def fake_switch_autoreboot(vmide, node):
    return {"status": "switch autoreboot OK"},200

def  test_valid_patch_vm_start(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    # client patch request with a body
    response = client.patch('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert response.status_code == 200
    assert response.json == {"status": "start OK"}

def  test_valid_patch_vm_reboot(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "reboot_vm", fake_reboot_vm)
    
    # client patch request with a body
    response = client.patch('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "reboot"})
    assert response.status_code == 200
    assert response.json == {"status": "reboot OK"}

def  test_valid_patch_vm_stop(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "stop_vm", fake_stop_vm)
    
    # client patch request with a body
    response = client.patch('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "stop"})
    assert response.status_code == 200
    assert response.json == {"status": "stop OK"}

def  test_valid_patch_vm_switch_autoreboot(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "switch_autoreboot", fake_switch_autoreboot)
    
    # client patch request with a body
    response = client.patch('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "switch_autoreboot"})
    assert response.status_code == 200
    assert response.json == {"status": "switch autoreboot OK"}

def  test_valid_patch_vm_unknown_status(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    # client patch request with a body
    response = client.patch('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "unknown"})
    assert response.status_code == 500
    assert response.json == {"status": "uknown status"}

# Try to patch the VM of another user
def test_foreign_patch_vm(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    # Not his vm
    response = client.patch('/api/1.0.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert response.status_code == 403

# Try to patch the VM as an admin
def test_admin_patch_vm(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    vm1 = client.patch('/api/1.0.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    vm2 = client.patch('/api/1.0.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert vm1.status_code == 200
    assert vm1.json == {"status": "start OK"}
    assert vm2.status_code == 200
    assert vm2.json == {"status": "start OK"}

# Try to patch with an invalid token
def test_invalid_patch_vm(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    
    
    # Not his vm
    response = client.patch('/api/1.0.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert response.status_code == 403



#####
## get_account_state
## get /account_state/{username}
#####

def fake_get_freeze_state(username):
    return {"freeze_state": "state"}, 200

def test_valid_get_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/api/1.0.0/account_state/user-1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 200
    assert response.json == {"freeze_state": "state"}

# invalid token
def test_invalid_get_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/api/1.0.0/account_state/user-1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403
    assert response.json == {"error": "Impossible to check your account. Please log into the MiNET cas"}

# get account state of another user
def test_foreign_get_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/api/1.0.0/account_state/user-2', headers={'Content-Type': 'application json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403
    assert response.json == {"error": "You are not allowed to check this account"}

# admin get its own account state
def test_admin_get_own_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/api/1.0.0/account_state/admin', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 200
    assert response.json == {"freezeState" : "0"}


# admin get other account state
def test_admin_get_other_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    user1 = client.get('/api/1.0.0/account_state/user-1', headers={'Content-Type': 'application json', "Authorization" : "Bearer AT-TEST"})
    user2 = client.get('/api/1.0.0/account_state/user-2', headers={'Content-Type': 'application json', "Authorization" : "Bearer AT-TEST"})
    print("user1", user1.json)
    assert user1.status_code == 200
    assert user1.json == {"freeze_state": "state"}
    assert user2.status_code == 200
    assert user2.json == {"freeze_state": "state"}
    