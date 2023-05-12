import pytest
from proxmox_api import proxmox
from test.conftest import *

stopped_func = []


# mocking func
def mock_stop_vm(vm_id, node):
    stopped_func.append(vm_id)
    return True


def mock_get_node_from_vm(vmid):
    return "node1", 200


def mock_get_proxmox_vm_status(vmid, node):
    if vmid == 5:
        return {"status": "stopped"}, 200
    return {"status": "running"}, 200


def test_stop_expired_vm(init_user_database, init_expired_vm_database, monkeypatch):
    monkeypatch.setattr(proxmox, "stop_vm", mock_stop_vm)
    monkeypatch.setattr(proxmox, "get_node_from_vm", mock_get_node_from_vm)
    monkeypatch.setattr(proxmox, "get_proxmox_vm_status", mock_get_proxmox_vm_status)
    proxmox.stop_expired_vm(flask_app.app)
    assert 3 in stopped_func
    assert 4 in stopped_func
