import pytest
from proxmox_api import proxmox
from test.conftest import *
from proxmox_api.db import db_functions




def test_creation_for_new_user(monkeypatch,init_user_database, init_vm_database, proxmoxAPI):
    """Test case for creation of VM by a new user
    The creation does not concern proxmox
    """

    node = "wammu"

    def fake_next_available_vmid():
        return "999"

    def fake_set_new_vm_ip(next_vmid, node):
        return "127.0.0.1"
    
    def fake_load_balance_server():
        return {'server' :'wammu'},201

    def fake_proxmox_clone_vm(name, newid,target, full):
        return True 
    
    def fake_vm_config(vmid, node, password, vm_user,main_ssh_key, ip):
        return True

    def fake_check_update_cotisation(user_id):
        return {"freezeState": "1"}, 200
    
    

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        # Mocking 
        monkeypatch.setattr(proxmox, 'next_available_vmid', fake_next_available_vmid)
        monkeypatch.setattr(proxmox, 'set_new_vm_ip', fake_set_new_vm_ip)
        monkeypatch.setattr(proxmoxAPI.nodes("wammu").qemu(10003).clone, 'create', fake_proxmox_clone_vm)
        monkeypatch.setattr(proxmox, 'load_balance_server', fake_load_balance_server)
        monkeypatch.setattr(proxmox, 'config_vm', fake_vm_config)
        monkeypatch.setattr(proxmox, 'check_update_cotisation', fake_check_update_cotisation)

        userId = "new-user"
        body,status = proxmox.create_vm("INTEGRATION-TEST-VM",  "bare_vm", userId, password="1A#aaaaaaaaa",  vm_user="user", main_ssh_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key")
        assert status == 201
        userVms = db_functions.get_user_list(user_id=userId)
        assert len(userVms) == 1



    

    


    







    
