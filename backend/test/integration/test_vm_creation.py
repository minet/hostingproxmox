import pytest
import proxmox_api.proxmox  as proxmox
import time
import proxmox_api.util as util
from flask_sqlalchemy import SQLAlchemy
from time import sleep


def test_valid_vm_creation(monkeypatch, init_database):
    """Test case for vm_creation. The vm configuration is also tested 
    """
    
    def fake_next_available_vmid():
        return 9998

    def fake_set_new_vm_ip(next_vmid, node):
        return "127.0.0.1"

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        # Mocking 
        monkeypatch.setattr(proxmox, 'next_available_vmid', fake_next_available_vmid)
        monkeypatch.setattr(proxmox, 'set_new_vm_ip', fake_set_new_vm_ip)



        body,status = proxmox.create_vm("INTEGRATION-TEST-VM",  "bare_vm", "valid-user", password="1A#aaaaaaaaa",  vm_user="user", main_ssh_key="ssh-key fake fake@key")
        assert status == 201 
        start_time = time.time()
        configuration_state = "creating"
        while time.time() - start_time <= 600 and   configuration_state != "": # timeout after 10min
            configuration_state = util.get_vm_state(9998)
            sleep(1)
        assert configuration_state == "created"


   