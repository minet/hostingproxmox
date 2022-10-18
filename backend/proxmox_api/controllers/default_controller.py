from email import header
from logging import error
from backend import proxmox_api
import connexion
import requests
import json
from requests.api import head
from slugify import slugify
from proxmox_api import proxmox
from proxmox_api.models.dns_entry_item import DnsEntryItem  # noqa: E501
from proxmox_api.models.dns_item import DnsItem  # noqa: E501
from proxmox_api.models.vm_id_item import VmIdItem  # noqa: E501
from proxmox_api.models.vm_item import VmItem  # noqa: E501
from proxmox_api import util
from proxmox_api.db.db_functions import *
from datetime import datetime
import proxmox_api.db.db_functions as dbfct
from proxmox_api.proxmox import is_admin
from threading import Thread


def create_dns(body=None):  # noqa: E501
    """create dns entry

     # noqa: E501
     The entry checks is made by util.py here, the dns ip ownership by proxmox.py and ip availability by ddns.py

    :param body: Dns entry to add
    :type body: dict | bytes

    :rtype: None
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"error": "You seem to be not connected."}, 403

    admin = False
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                admin = True;
    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState != 0 and not admin:
        return {"error": "Your cotisation has expired"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    if connexion.request.is_json:
        body = DnsItem.from_dict(connexion.request.get_json())  # noqa: E501

   # finally we have to check if the entry is correct : 
    if not util.check_dns_entry(body.entry):
        print("INCIDENT REPORT : The user ( id " , str(user_id) , ") overrided frontend security to submit a forbidden DNS entry : " , body.entry, "for ip", body.ip  )
        return {"error" : "This DNS entry is forbidden. This incident will be reported."}, 403

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
        return {"error": "Your are not allowed to be here"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    admin = False
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                admin = True;
    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState != 0 and not admin: # for any other freestate user can't create vm
        return {"error": "Your cotisation has expired"}, 403

    if connexion.request.is_json:
        body = VmItem.from_dict(connexion.request.get_json())  # noqa: E501

    if not util.check_password_strength(body.password):
        return {"error" : "Incorrect password format"}, 400
    if not util.check_ssh_key(body.ssh_key):
        return {"error" : "Incorrect ssh key format"}, 400
    if not util.check_username(body.user):
        return {"error" : "Incorrect vm user format"}, 400

    return proxmox.create_vm(body.name, body.type, user_id, body.password, body.user, body.ssh_key)


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

    admin = False
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                admin = True;
    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # if freeze state 1 or 2 user still have access to proxmox
        return {"status": "cotisation expired"}, 403

    node = proxmox.get_node_from_vm(vmid)
    if not node:
        return {"status": "vm not exists"}, 404
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                return proxmox.delete_vm(vmid, node)
    if vmid in map(int, proxmox.get_vm(user_id)[0]):
        return proxmox.delete_vm(vmid, node)
    else:
        return {"status": "error"}, 500

################
## DEPRECATED ##
################
# Reason : must be remplaced by the freeze state
def is_cotisation_uptodate():
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    if r.status_code != 200:
        return {"Error": "You are UNAUTHORIZED to connect to CAS"}, 403
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                return {"status": "function denied for admin"}, 403

    id = r.json()['attributes']['id']

    r = requests.get("https://adh6.minet.net/api/member/" + id, headers=headers)

    if r.status_code != 200:
        return {"Error": "You are UNAUTHORIZED to connect to adh6"}, 403

    strdate = r.json()['departureDate']
    date = datetime.strptime(strdate, '%Y-%m-%d')
    if date > datetime.today():
        return {"uptodate": 1}, 201;
    else:
        return {"uptodate": 0}, 201;


def get_dns():  # noqa: E501
    """check if a user has signed the hosting charter

     # noqa: E501


    :rtype: List[DnsEntryItem]
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)

    if r.status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                admin = True;
    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 and 2, the user still can be connected to hosting
        return {"status": "cotisation expired"}, 403

   

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                return proxmox.get_user_dns()

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
    admin = False
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                admin = True;
    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"error": "cotisation expired"}, 403



    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                return proxmox.get_vm()  # affichage de la liste sans condition
    return proxmox.get_vm(user_id=user_id)


def get_vm_id(vmid):  # noqa: E501
    """get a vm by id

     # noqa: E501

    :param vmid: vmid to get
    :type vmid: string

    :rtype: VmItem
    """
    start = time.time()
    print("backend api called " , vmid)


    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    
    if r.status_code != 200:
        return {"error": "Impossible to check your account. Please log into the MiNET cas"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    print(statusCode)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3: # For freeze state 1 or 2, the user can access to hosting
        return {"error": "cotisation expired"}, 403

    admin = False

    try:
        vmid = int(vmid)
    except:
        return {"error": "The request contains errors"}, 400

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    if not vmid in map(int, proxmox.get_vm(user_id)[0]) and not admin:
        return {"error": "You don't have the right permissions"}, 403

    node = proxmox.get_node_from_vm(vmid)
    print("node recieved :", node)
    if not node:
        return {"error": "Impossible to retrieve the vm"}, 404

    status = proxmox.get_vm_status(vmid, node)
    type = dbfct.get_vm_type(vmid)
    created_on = get_vm_created_on(vmid)


    proxmoxStart = time.time()
    (vmConfig, response) = proxmox.get_vm_config(vmid, node)
    #print("get_vm_config for " , vmid , " took ")

    print("(vmConfig, response) = ", (vmConfig, response))

    if response == 500:
        print("500 error, vmConfig = ", vmConfig)
        return vmConfig, 500
        print("500 ended")
    elif response == 404:
        return {"error": "VM not found"},404
    elif response == 200 or( response == 201 and 'status' in vmConfig.keys()): # If the returned code is 201 and the vm is just created
        return vmConfig, response
    elif response != 201 :
        return {"error": "API unkonwn response"},500
    try:
        name = vmConfig["name"]
        ram = vmConfig["ram"]
        cpu = vmConfig["cpu"]
        disk = vmConfig["disk"]
        autoreboot = vmConfig["autoreboot"]
    except Exception as e:
        print("error while getting config : " + str(e))
        return {"error": "error while getting config : " + str(e)}, 500

   # print("recieved config response (" ,vmid ,") ok. Took" , str(time.time() - start))

    owner = get_vm_userid(vmid)  # on renvoie l'owner pour que les admins puissent savoir à quel user appartient quelle vm

    if status[0]["status"] != 'running':
        return {"name": name, "autoreboot": autoreboot, "user": owner if admin else "", "ip": "", "status": status[0]["status"],
                "ram": ram, "cpu": cpu, "disk": disk, "type": type[0]["type"],
                "ram_usage": 0, "cpu_usage": 0, "uptime": 0, "created_on": created_on[0]["created_on"]}, 201
    else:
        ip = proxmox.get_vm_ip(vmid, node)
        current_status,response = proxmox.get_vm_current_status(vmid, node)

        #print("recieved status response (" ,vmid ,") ok. Took" , str(time.time() - start))

        if response == 500:
            return vmConfig, 500
        elif response == 404:
            return {"error": "VM not found"},404
        elif response != 201:
            return {"error": "API unkonwn response"},500
        try:
            cpu_usage = current_status["cpu_usage"]
            ram_usage = current_status["ram_usage"]
            uptime = current_status["uptime"]
        except:
            return {"status": "error while getting current status"}, 500


    #print("backend api vm (" ,vmid ,") ok. Took" , str(time.time() - start))
    if  (status[1] == 201 or status[1] == 200) and (type[1] == 201 or type[1] == 200) and (ip[1] == 201 or ip[1] == 200):
        return {"name": name, "autoreboot": autoreboot, "user": owner if admin else "", "ip": ip[0]["vm_ip"]
                   , "status": status[0]["status"], "ram": ram
                   , "cpu": cpu, "disk": disk, "type": type[0]["type"]
                   , "ram_usage": ram_usage, "cpu_usage": cpu_usage
                   , "uptime": uptime, "created_on": created_on[0]["created_on"]}, 201

    elif   status[1] == 404 or type[1] == 404 or ip[1] == 404 :
        return {"error": "vm not found"}, 404
    else:
        print("datal error for vm ", vmid, "Unknown error one of the status, type or ip doesn't exists : ", status, type, ip)
        return {"error": "Unknown error one of the status, type or ip doesn't exists."}, 500


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

    admin = False
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                admin = True;
    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"status": "cotisation expired"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                return proxmox.del_user_dns(dnsid)

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
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    if r.status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):
                admin = True;
    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"status": "cotisation expired"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    try:
        dnsid = int(dnsid)
    except:
        return {"status": "error not an integer"}, 500

    admin = False

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    entry = dbfct.get_entry_host(dnsid)
    ip = dbfct.get_entry_ip(dnsid)
    owner = dbfct.get_entry_userid(dnsid)
    if entry[1] == 201 and ip[1] == 201:
        return {"ip": ip[0]['ip'], "entry": entry[0]['host'], "user": owner if admin else ""}, 201
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

    admin = False

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"status": "cotisation expired"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))

    if vmid in map(int, proxmox.get_vm(user_id)[0]) or admin:
        node = proxmox.get_node_from_vm(vmid)
        if not node:
            return {"status": "vm not exists"}, 404
        if body.status == "start":
            return proxmox.start_vm(vmid, node)
        elif body.status == "stop":
            return proxmox.stop_vm(vmid, node)
        elif body.status == "switch_autoreboot":
            return proxmox.switch_autoreboot(vmid, node)
        else:
            return {"status": "error"}, 500
    else:
        return {"status": "error"}, 500

def get_historyip(vmid):
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    if r.status_code != 200:
        return {"status": "error"}, 403

    admin = False

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    if admin == True:
        return get_historyip_fromdb(vmid)
    else:
        return {"status": "error"}, 403

def get_historyipall():
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    if r.status_code != 200:
        return {"status": "error"}, 403

    admin = False

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    if admin == True:
        return get_historyip_fromdb()
    else:
        return {"status": "error"}, 403


# Return the list of all ips of a user

def get_ip_list():
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    if r.status_code != 200:
        return {"status": "This is forbidden"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))
    body,statusCode = proxmox.get_freeze_state(user_id)
    if statusCode != 200:
        return body, statusCode
    try:
        freezeAccountState = int(body["freezeState"])
        print(freezeAccountState)
    except Exception as e:
        return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3: # if freeze state 1 or 2 the user can access to proxmox
        return {"status": "cotisation expired"}, 403

    list = proxmox.get_user_ip_list(r.json()["id"])
    if list == None:
        return {"status": "Impossible to retrieve the list of your ip addresses. Please make juste you have at least one."}, 500
    else : 
        return {"ip_list": list}, 200


def get_account_state(username):
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=headers)
    
    if r.status_code != 200:
        return {"error": "Impossible to check your account. Please log into the MiNET cas"}, 403

    user_id = slugify(r.json()['sub'].replace('_', '-'))
    admin = False

    if "attributes" in r.json():
        if "memberOf" in r.json()["attributes"]:
            if is_admin(r.json()["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True
    if not admin and user_id != username:
        return {"error": "You are not allowed to check this account"}, 403
    return proxmox.get_freeze_state(username)
