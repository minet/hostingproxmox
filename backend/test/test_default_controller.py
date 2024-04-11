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
    return "wammu",200
def fake_get_proxmox_vm_status(vmid, node):
    return {"status": "running"}, 201
def fake_get_vm_config(vmid, node):
        return  {"name": "test", "ram" : "4", "cpu":"2", "autoreboot" : "1", "disk" : "30"},201
def fake_get_vm_current_status(vmid, node):
        return  {"cpu_usage": "2", "ram_usage" : "4", "uptime":"2"},201
def fake_get_vm_ip(vmid, node):
        return  {"vm_ip": "157.159.195.256"},201
def fake_get_freeze_state(username):
    return {"freezeState": "0"}, 200
def fake_get_expired_freeze_state(username):
    return {"freezeState": "1"}, 200
def fake_create_vm(name, type, user_id, cpu, ram, disk, password, user, sshKey ):
    return "ok", 201


#####
## get_vm_id
## GET /2.0/vm/{vmid}
#####


# Valid user with valid token. Not admin.
def test_valid_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):
    print("client1", client)
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
    monkeypatch.setattr(proxmox, "get_vm_current_status", fake_get_vm_current_status)
    monkeypatch.setattr(proxmox, "get_vm_ip", fake_get_vm_ip)
    response = client.get('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    print(response.json)
    assert response.status_code == 201

def test_valid_valid_get_vm_id_with_unsecure(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
    monkeypatch.setattr(proxmox, "get_vm_current_status", fake_get_vm_current_status)
    monkeypatch.setattr(proxmox, "get_vm_ip", fake_get_vm_ip)
    response = client.get('/2.0/vm/6', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    print("json=" ,response.json)
    assert response.status_code == 201
    assert response.json['unsecure'] == True

# Valid user with not valid token. Not admin.
def test_false_token_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):

    print("client2", client)

    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
    monkeypatch.setattr(proxmox, "get_vm_current_status", fake_get_vm_current_status)
    monkeypatch.setattr(proxmox, "get_vm_ip", fake_get_vm_ip)

    response = client.get('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert response.status_code == 403

#  valid user with a valid token. Not admin. Trying to access to another's vm.
def test_foreign_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):

    

    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
    monkeypatch.setattr(proxmox, "get_vm_current_status", fake_get_vm_current_status)
    monkeypatch.setattr(proxmox, "get_vm_ip", fake_get_vm_ip)

    response = client.get('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert response.status_code == 403

#  admin
def test_admin_get_vm_id(client, init_user_database, init_vm_database, monkeypatch):

    

    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", fake_get_proxmox_vm_status)
    monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
    monkeypatch.setattr(proxmox, "get_vm_current_status", fake_get_vm_current_status)
    monkeypatch.setattr(proxmox, "get_vm_ip", fake_get_vm_ip)

    vm1 = client.get('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    vm2 = client.get('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert vm1.status_code == 201
    assert vm2.status_code == 201



#####
## create_vm
## POST /2.0/vm
#####

# Valid user with valid token. Not admin.
def test_valid_create_vm(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [],200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({"cpu": 2, "ram": 2, "disk":2, "name":"test", "type":"bare", "password":"#1Aaaaaaaaaaa", "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key",  "user":"test"})
        )
     assert response.status_code == 201

def test_create_vm_id_with_expired_account(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [],200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_expired_freeze_state)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({"cpu": 2, "ram": 2, "disk":2, "name":"test", "type":"bare", "password":"#1Aaaaaaaaaaa", "user":"test", "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key"})
        )
     assert response.status_code == 403

def test_create_vm_without_arg(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [],200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({})
        )
     assert response.status_code == 400

def test_create_vm_without_ressources(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [],200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({"name":"test", "type":"bare", "password":"#1Aaaaaaaaaaa", "user":"test", "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key"})
        )
     assert response.status_code == 400

def test_create_vm_with_too_much_cpu(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [],200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({"cpu": 100, "ram": 2, "disk":2,"name":"test", "type":"bare", "password":"#1Aaaaaaaaaaa", "user":"test", "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key"})
        )
     assert response.status_code == 403
    
def test_create_vm_with_too_much_ram(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [],200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({"cpu": 2, "ram": 200, "disk":2,"name":"test", "type":"bare", "password":"#1Aaaaaaaaaaa", "user":"test", "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key"})
        )
     assert response.status_code == 403

def test_create_vm_with_too_much_storage(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [],200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({"cpu": 1, "ram": 2, "disk":200,"name":"test", "type":"bare", "password":"#1Aaaaaaaaaaa", "user":"test", "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key"})
        )
     assert response.status_code == 403

def test_create_vm_with_no_ressources_left(client, init_user_database, init_vm_database, init_max_ressources_for_one_user,monkeypatch):
     def fake_get_vm(user_id):
        return [100],200
     def get_vm_config(vmid, node):
        return {"cpu": 6, "ram": 9, "disk":30}, 200
     monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
     monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
     monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
     monkeypatch.setattr(proxmox, "get_vm_config", fake_get_vm_config)
     monkeypatch.setattr(proxmox, "get_vm", fake_get_vm)
     monkeypatch.setattr(proxmox, "create_vm", fake_create_vm)
     
     response = client.post(
         '/2.0/vm', 
         headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"}, 
         data=json.dumps({"cpu": 1, "ram": 2, "disk":200,"name":"test", "type":"bare", "password":"#1Aaaaaaaaaaa", "user":"test", "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key"})
        )
     assert response.status_code == 403

#####
## delete_vm_id
## delete /2.0/vm/{vmid}
#####

def fake_delete_vm_in_thread(vmid, user_id, node="", dueToError=False):
    return True

# Valid user with valid token. Not admin.
def test_valid_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):    
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 200


# Valid user with not valid token. Not admin.
def test_false_token_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403

#  valid user with a valid token. Not admin. Trying to delete an another's vm.
def test_foreign_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):    
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403

#  admin
def test_admin_delete_vm_id(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    vm1 = client.delete('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    vm2 = client.delete('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert vm1.status_code == 200
    assert vm2.status_code == 200




#####
## delete_vm_id with error
## delete /2.0/vmWithError/{vmid}
#####

def fake_delete_vm_in_thread(vmid, user_id, node="", dueToError=False):
    return True

# Valid user with valid token. Not admin.
def test_valid_delete_vm_with_error_id(client, init_user_database, init_vm_database, monkeypatch):    
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/2.0/vmWithError/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 200


# Valid user with not valid token. Not admin.
def test_false_token_delete_vm_with_error_id(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/2.0/vmWithError/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403

#  valid user with a valid token. Not admin. Trying to delete an another's vm.
def test_foreign_delete_vm_with_error_id(client, init_user_database, init_vm_database, monkeypatch):    
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    response = client.delete('/2.0/vmWithError/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403

#  admin
def test_admin_delete_vm_with_error_id(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(default_controller, "delete_vm_in_thread", fake_delete_vm_in_thread)
    
    vm1 = client.delete('/2.0/vmWithError/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    vm2 = client.delete('/2.0/vmWithError/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert vm1.status_code == 200
    assert vm2.status_code == 200





#####
## patch_vm
## patch /2.0/vm/{vmid}
#####

def fake_start_vm(vmide, node):
    return {"status": "start OK"},200

def fake_reboot_vm(vmide, node):
    return {"status": "reboot OK"},200

def fake_stop_vm(vmide, node):
    return {"status": "stop OK"},200

def fake_switch_autoreboot(vmide, node):
    return {"status": "switch autoreboot OK"},200

def fake_transfer_ownership(vmid, new_owner):
    if new_owner == "" or new_owner == None :
        return {"error": "No login given"}, 400
    return {"status": "OK"},200

def  test_valid_patch_vm_start(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    # client patch request with a body
    response = client.patch('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert response.status_code == 200
    assert response.json == {"status": "start OK"}

def  test_valid_patch_vm_reboot(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "reboot_vm", fake_reboot_vm)
    
    # client patch request with a body
    response = client.patch('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "reboot"})
    assert response.status_code == 200
    assert response.json == {"status": "reboot OK"}

def  test_valid_patch_vm_stop(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "stop_vm", fake_stop_vm)
    
    # client patch request with a body
    response = client.patch('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "stop"})
    assert response.status_code == 200
    assert response.json == {"status": "stop OK"}

def  test_valid_patch_vm_switch_autoreboot(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "switch_autoreboot", fake_switch_autoreboot)
    
    # client patch request with a body
    response = client.patch('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "switch_autoreboot"})
    assert response.status_code == 200
    assert response.json == {"status": "switch autoreboot OK"}

def  test_valid_patch_vm_unknown_status(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    # client patch request with a body
    response = client.patch('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "unknown"})
    assert response.status_code == 500
    assert response.json == {"status": "uknown status"}

# Try to patch the VM of another user
def test_foreign_patch_vm(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    # Not his vm
    response = client.patch('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert response.status_code == 403

# Try to patch the VM as an admin
def test_admin_patch_vm(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "start_vm", fake_start_vm)
    
    vm1 = client.patch('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    vm2 = client.patch('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert vm1.status_code == 200
    assert vm1.json == {"status": "start OK"}
    assert vm2.status_code == 200
    assert vm2.json == {"status": "start OK"}

# Try to transfert the VM as an admin
def test_admin_transfer_ownership(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "transfer_ownership", fake_transfer_ownership)
    
    vm1 = client.patch('/2.0/vm/3', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "transfering_ownership", "user" : "user-1"})
    assert vm1.status_code == 200
    assert vm1.json == {"status": "OK"}

# Try to transfert the VM as an a non admin
def test_non_admin_transfer_ownership(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    monkeypatch.setattr(proxmox, "transfer_ownership", fake_transfer_ownership)
    
    vm1 = client.patch('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "transfering_ownership", "user" : "user-1"})
    assert vm1.status_code == 403
    assert vm1.json == {"status": "Permission denied"}

# Try to patch with an invalid token
def test_invalid_patch_vm(client, init_user_database, init_vm_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_node_from_vm", fake_get_node_from_vm)
    
    
    # Not his vm
    response = client.patch('/2.0/vm/1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"}, json={"status": "start"})
    assert response.status_code == 403



#####
## get_account_state
## get /account_state/{username}
#####



def test_valid_get_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/2.0/account_state/user-1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 200
    assert response.json == {"freezeState": "0"}

# invalid token
def test_invalid_get_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token_fail)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/2.0/account_state/user-1', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403
    assert response.json == {"error": "Impossible to check your account. Please log into the MiNET cas"}

# get account state of another user
def test_foreign_get_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/2.0/account_state/user-2', headers={'Content-Type': 'application json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 403
    assert response.json == {"error": "You are not allowed to check this account"}

# admin get its own account state
def test_admin_get_own_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    response = client.get('/2.0/account_state/admin', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-TEST"})
    assert response.status_code == 200
    assert response.json == {"freezeState" : "0"}


# admin get other account state
def test_admin_get_other_account_state(client, init_user_database, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)
    monkeypatch.setattr(proxmox, "get_freeze_state", fake_get_freeze_state)
    
    user1 = client.get('/2.0/account_state/user-1', headers={'Content-Type': 'application json', "Authorization" : "Bearer AT-TEST"})
    user2 = client.get('/2.0/account_state/user-2', headers={'Content-Type': 'application json', "Authorization" : "Bearer AT-TEST"})
    print("user1", user1.json)
    assert user1.status_code == 200
    assert user1.json == {"freezeState": "0"}
    assert user2.status_code == 200
    assert user2.json == {"freezeState": "0"}


def test_list_freezed_account(monkeypatch,init_user_database, client):
    """Test if every freezed account is listed

    """
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_admin)

    response = client.get('/2.0/expired', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    print(response.json)
    assert response.status_code == 200
    assert response.json == ["expired-user-3", "expired-user-4"]    



#####
## get_account_max_ressources
## get /max_account_ressources
#####


def test_valide_ressources_fetchdef(client, init_max_ressources_for_one_user, monkeypatch):
    monkeypatch.setattr(util, "check_cas_token", fake_check_cas_token)
    response = client.get('/2.0/max_account_ressources', headers={'Content-Type': 'application/json', "Authorization" : "Bearer AT-232-ZAlr3TdJmZbGkL173Al8xm1VWSPnJTpy"})
    assert response.status_code == 200