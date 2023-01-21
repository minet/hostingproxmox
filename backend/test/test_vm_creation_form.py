import pytest
from proxmox_api import proxmox
from test.conftest import *
from proxmox_api.db import db_functions
from proxmoxer import ProxmoxAPI

def fake_next_available_vmid():
        return "999"

def fake_set_new_vm_ip(next_vmid, node):
    return "127.0.0.1"

def fake_load_balance_server():
    return {'server' :'wammu'},201
def fake_proxmox_clone_vm(name, newid,target, full):
    return True 

def fake_vm_config(vmid, node, password, vm_usermain_ssh_key, ip):
    return True
def fake_check_update_cotisation(user_id):
    return {"freezeState": "1"}, 200



def fake_config_vm(next_vmid, node, password, vm_user, main_ssh_key,ip):
    return True

class _ProxmoxAPIRessources:
    def __init__(self):
        pass

    def get(*args, **kwargs):
        return [{"vmid": "10003", "node":"kars"}]

class _ProxmoxAPIcluster:
    def __init__(self):
        pass

    resources = _ProxmoxAPIRessources()


class _ProxmoxAPIClone:
    def __init__(self):
        pass

    def create(*args, **kwargs):
        return True
class _ProxmoxAPIQemu:
    clone = _ProxmoxAPIClone()
    def __init__(self):
        pass


class _ProxmoxAPINode:
    def __init__(self):
        pass

    def qemu(self, vmid):
        return _ProxmoxAPIQemu()
    

class _ProxmoxAPI:
    def __init__(self, node, monkeypatch):
        pass
    cluster = _ProxmoxAPIcluster()

    def nodes(self, node):
        return _ProxmoxAPINode()


    


def test_creation_for_new_user(monkeypatch,init_user_database, init_vm_database):
    """Test case for creation of VM by a new user
    The creation does not concern proxmox
    """

    node = "wammu"
    
    

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        # Mocking 
        monkeypatch.setattr(proxmox, 'next_available_vmid', fake_next_available_vmid)
        monkeypatch.setattr(proxmox, 'set_new_vm_ip', fake_set_new_vm_ip)
        
        """proxmoxapi = ProxmoxAPI(host=configuration.PROXMOX_HOST, user=configuration.PROXMOX_USER
                     , token_name=configuration.PROXMOX_API_KEY_NAME
                     , token_value=configuration.PROXMOX_API_KEY, verify_ssl=False)
"""
        #monkeypatch.setattr(proxmox.proxmox.nodes("kars").qemu(10003).clone,'create', fake_proxmox_clone_vm)
        node="kars"
        realProxmox = proxmox.proxmox
        proxmox.proxmox = _ProxmoxAPI(node, monkeypatch)
        
        #monkeypatch.setattr(proxmox.proxmox, "nodes", lambda self, node: _ProxmoxAPI(node, monkeypatch))
        monkeypatch.setattr(proxmox, 'load_balance_server', fake_load_balance_server)
        monkeypatch.setattr(proxmox, 'config_vm', fake_vm_config)
        monkeypatch.setattr(proxmox, 'check_update_cotisation', fake_check_update_cotisation)
        monkeypatch.setattr(proxmox, 'config_vm', fake_config_vm)

        userId = "new-user6"
        body,status = proxmox.create_vm("INTEGRATION-TEST-VM",  "bare_vm", userId, password="1A#aaaaaaaaa",  vm_user="user", main_ssh_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key")
        proxmox.proxmox = realProxmox
        assert status == 201
        userVms = db_functions.get_vm_list(user_id=userId)
        assert len(userVms) == 1



    



    







    
