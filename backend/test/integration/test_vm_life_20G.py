import pytest
import proxmox_api.proxmox as proxmox
import time
import proxmox_api.util as util
from flask_sqlalchemy import SQLAlchemy
from time import sleep


VMID = 9998
DISK_SIZE = 20


@pytest.mark.dependency(name="clean")
def test_old_vm_deletion(init_vm_database):
    """Test in charge of destroying all vm test created in the past."""
    node, status = proxmox.get_node_from_vm(VMID)
    print(node)
    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    doesVMexist = False
    with app.app.app_context():
        if status == 200:
            doesVMexist = True
        if doesVMexist:
            assert node == "kars" or node == "wammu"
            r = proxmox.delete_from_proxmox(VMID, node)
            assert r == True
        else:
            assert True


# If previous test fail, we do not try to create a new one


@pytest.mark.dependency(name="creation", depends=["clean"])
def test_valid_vm_creation(monkeypatch, init_user_database, init_vm_database):
    """Test case for vm_creation. The vm configuration is also tested"""

    def fake_next_available_vmid():
        return VMID

    def fake_set_new_vm_ip(next_vmid, node):
        return "127.0.0.1"

    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        # Mocking
        monkeypatch.setattr(proxmox, "next_available_vmid", fake_next_available_vmid)
        monkeypatch.setattr(proxmox, "set_new_vm_ip", fake_set_new_vm_ip)

        body, status = proxmox.create_vm(
            "INTEGRATION-TEST-VM",
            "bare_vm",
            "valid-user",
            2,
            4,
            DISK_SIZE,
            password="1A#aaaaaaaaa",
            vm_user="user",
            main_ssh_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWkpOTUuLKpZEQT2CmEsgZwZzegitYCx/8vHICvv261 fake@key",
        )
        assert status == 201
        start_time = time.time()
        configuration_state = "creating"
        while (
            time.time() - start_time <= 600 and configuration_state == "creating"
        ):  # timeout after 10min
            configuration_state, _, _ = util.get_vm_state(VMID)
            sleep(1)
        assert configuration_state == "created"


# If previous test fail, we do not try to start it
@pytest.mark.dependency(name="start", depends=["clean", "creation"])
def test_vm_start():
    """Test case for vm_start"""
    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        node, status_node = proxmox.get_node_from_vm(VMID)
        body, status_start = proxmox.start_vm(VMID, node)
        assert status_node == 200
        assert status_start == 201


# If previous test fail, we do not try to start it
@pytest.mark.dependency(name="stop", depends=["clean", "creation", "start"])
def test_vm_stop():
    """Test case for vm_start"""
    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        node, status_node = proxmox.get_node_from_vm(VMID)
        body, status_stop = proxmox.stop_vm(VMID, node)
        assert status_node == 200
        assert status_stop == 201


# If previous test fail, we do not try to start it
@pytest.mark.dependency(name="delete", depends=["clean", "creation", "start", "stop"])
def test_vm_deletion():
    """Test case for vm_start"""
    app = util.create_app()
    db = SQLAlchemy()
    db.init_app(app.app)
    with app.app.app_context():
        node, status_node = proxmox.get_node_from_vm(VMID)
        isProxmoxDeleted = proxmox.delete_from_proxmox(VMID, node)
        isDbDeleted = proxmox.delete_from_db(VMID)
        assert status_node == 200
        assert isProxmoxDeleted
        assert isDbDeleted
