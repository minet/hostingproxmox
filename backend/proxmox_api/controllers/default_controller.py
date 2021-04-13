import connexion
import requests
from slugify import slugify
from proxmox_api import proxmox
from proxmox_api.models.dns_entry_item import DnsEntryItem  # noqa: E501
from proxmox_api.models.dns_item import DnsItem  # noqa: E501
from proxmox_api.models.vm_id_item import VmIdItem  # noqa: E501
from proxmox_api.models.vm_item import VmItem  # noqa: E501
from proxmox_api import util
from proxmox_api.db.db_functions import *

import proxmox_api.db.db_functions as dbfct

def create_dns(body=None):  # noqa: E501
    """create dns entry

     # noqa: E501

    :param body: Dns entry to add
    :type body: dict | bytes

    :rtype: None
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    if connexion.request.is_json:
        body = DnsItem.from_dict(connexion.request.get_json())  # noqa: E501

    return proxmox.add_user_dns(user_id, body.entry, body.ip)


def create_vm(body=None):  # noqa: E501
    """create vm

     # noqa: E501

    :param body: VM to create
    :type body: dict | bytes

    :rtype: None
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    if r.status_code != 200:
        return {"status": "error"}, 403

    if connexion.request.is_json:
        body = VmItem.from_dict(connexion.request.get_json())  # noqa: E501

    if body.ssh:
        return proxmox.create_vm(body.name, body.type, user_id, body.password, body.user, body.ssh_key)
    else:
        return proxmox.create_vm(body.name, body.type, user_id, body.password, body.user)


def delete_vm_id(vmid):  # noqa: E501
    """delete vm by id

     # noqa: E501

    :param vmid: vmid to get
    :type vmid: float

    :rtype: None
    """
    try:
        vmid = int(vmid)
    except:
        return {"status": "error not an integer"}, 500

    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))
    if user_id in ("seberus","zastava","lionofinterest") :
        return proxmox.delete_vm(vmid)
    if vmid in map(int, proxmox.get_vm(user_id)[0]):
        return proxmox.delete_vm(vmid)
    else:
        return {"status": "error"}, 500


def get_dns():  # noqa: E501
    """get all user&#x27;s dns entries

     # noqa: E501


    :rtype: List[DnsEntryItem]
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))
    return proxmox.get_user_dns(user_id)

def get_vm():  # noqa: E501
    """get all user vms

     # noqa: E501


    :rtype: List[VmIdItem]
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))
    if user_id in ("seberus","zastava","lionofinterest") :
        return proxmox.get_vm()
    return proxmox.get_vm(user_id=user_id)

def get_vm_id(vmid, admin = False):  # noqa: E501
    """get a vm by id

     # noqa: E501

    :param vmid: vmid to get
    :type vmid: string

    :rtype: VmItem
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    try:
        vmid = int(vmid)
    except:
        return {"status": "error not an integer"}, 500
    status = proxmox.get_vm_status(vmid)
    type = dbfct.get_vm_type(vmid)

    if status[0]["status"] == 'creating':
        return {"status": status[0]["status"], "type": type[0]["type"]}, 201

    name = proxmox.get_vm_name(vmid)
    ram = proxmox.get_vm_ram(vmid)
    cpu = proxmox.get_vm_cpu(vmid)
    disk = proxmox.get_vm_disk(vmid)
    if user_id in ("seberus","zastava","lionofinterest") :
        owner = get_vm_userid(vmid)
        if status[0]["status"] != 'running':
            return {"name": name[0]["name"], "owner": owner, "ip": None, "status": status[0]["status"], "ram": ram[0]['ram']
                       ,"cpu": cpu[0]["cpu"], "disk": disk[0]["disk"], "type": type[0]["type"]}, 201

        ip = proxmox.get_vm_ip(vmid)

        if name[1] == 201 and ip[1] == 201 and status[1] == 201 and ram[1] == 201 and cpu[1] == 201 and disk[1] == 201 and \
                type[1] == 201:
            return {"name": name[0]["name"], "owner": owner, "ip": ip[0]["vm_ip"], "status": status[0]["status"], "ram": ram[0]['ram']
                       , "cpu": cpu[0]["cpu"], "disk": disk[0]["disk"], "type": type[0]["type"]}, 201
        elif name[1] == 404 or ip[1] == 404 or status[1] == 404 or ram[1] == 404 or disk[1] == 404 or cpu[1] == 404 or type[
            1] == 404:
            return {"status": "vm not found"}, 404
        else:
            return {"status": "error"}, 500
    else:
        if status[0]["status"] != 'running':
            return {"name": name[0]["name"], "ip": None, "status": status[0]["status"], "ram": ram[0]['ram']
                       , "cpu": cpu[0]["cpu"], "disk": disk[0]["disk"], "type": type[0]["type"]}, 201

        ip = proxmox.get_vm_ip(vmid)

        if name[1] == 201 and ip[1] == 201 and status[1] == 201 and ram[1] == 201 and cpu[1] == 201 and disk[
            1] == 201 and \
                type[1] == 201:
            return {"name": name[0]["name"], "ip": ip[0]["vm_ip"], "status": status[0]["status"], "ram": ram[0]['ram']
                       , "cpu": cpu[0]["cpu"], "disk": disk[0]["disk"], "type": type[0]["type"]}, 201
        elif name[1] == 404 or ip[1] == 404 or status[1] == 404 or ram[1] == 404 or disk[1] == 404 or cpu[1] == 404 or \
                type[
                    1] == 404:
            return {"status": "vm not found"}, 404
        else:
            return {"status": "error"}, 500

def delete_dns_id(dnsid):  # noqa: E501
    """delete dns entry by id

     # noqa: E501

    :param id: id of the dns entry to delete
    :type id: str

    :rtype: None
    """
    try:
        dnsid = int(dnsid)
    except:
        return {"status": "error not an integer"}, 500

    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    if dnsid in map(int, proxmox.get_user_dns(user_id)[0]):
        return proxmox.del_user_dns(dnsid)
    else:
        return {"status": "error"}, 500


def get_dns_id(dnsid):  # noqa: E501
    """get a dns entry by id

     # noqa: E501

    :param id: id of the dns entry entry to get
    :type id: str

    :rtype: DnsItem
    """
    try:
        dnsid = int(dnsid)
    except:
        return {"status": "error not an integer"}, 500

    entry = dbfct.get_entry_host(dnsid)
    ip = dbfct.get_entry_ip(dnsid)

    if entry[1] == 201 and ip[1] == 201:
        return {"ip": ip[0]['ip'], "entry": entry[0]['host']}, 201
    elif entry[1] == 404 or ip[1] == 404:
        return {"status": "dns entry not found"}, 404
    else:
        return {"status": "error"}, 500


def patch_vm(vmid, body=None):  # noqa: E501
    """update a vm

     # noqa: E501

    :param vmid: vmid to update
    :type vmid: str
    :param body: VM to update
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = VmItem.from_dict(connexion.request.get_json())  # noqa: E501

    try:
        vmid = int(vmid)
    except:
        return {"status": "error not an integer"}, 500

    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    if r.status_code != 200:
        return {"status": "error"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    if vmid in map(int, proxmox.get_vm(user_id)[0]) or user_id in ("seberus","zastava","lionofinterest") :
        if body.status == "start":
            return proxmox.start_vm(vmid)
        elif body.status == "stop":
            return proxmox.stop_vm(vmid)
        else:
            return {"status": "error"}, 500
    else:
        return {"status": "error"}, 500