from logging import error
from proxmox_api import proxmox
import connexion
import requests
import json
from threading import Thread
from requests.api import head
from slugify import slugify
from proxmox_api.models.dns_entry_item import DnsEntryItem  # noqa: E501
from proxmox_api.models.dns_item import DnsItem  # noqa: E501
from proxmox_api.models.vm_id_item import VmIdItem  # noqa: E501
from proxmox_api.models.vm_item import VmItem  # noqa: E501
from proxmox_api import util
from proxmox_api.db.db_functions import *
from datetime import datetime
import proxmox_api.db.db_functions as dbfct
from proxmox_api.proxmox import is_admin


def create_dns(body=None):  # noqa: E501
    """create dns entry

     # noqa: E501
     The entry checks is made by util.py here, the dns ip ownership by proxmox.py and ip availability by ddns.py

    :param body: Dns entry to add
    :type body: dict | bytes

    :rtype: None
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"error": "You seem to be not connected."}, 403
    user_id = cas['sub']
    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True
                
    if admin :
        freezeAccountState = 0 # Un admin n'a pas d'expiration de compte
    else :
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
    
    if freezeAccountState != 0 and not admin:
        return {"error": "Your cotisation has expired"}, 403

    user_id = cas['sub']

    if connexion.request.is_json:
        body = DnsItem.from_dict(connexion.request.get_json())  # noqa: E501

   # finally we have to check if the entry is correct : 
    if not util.check_dns_entry(body.entry):
        print("INCIDENT REPORT : The user ( id " , str(user_id) , ") overrided frontend security to submit a forbidden DNS entry : " , body.entry, "for ip", body.ip  )
        return {"error" : "This DNS entry is forbidden. This incident will be reported."}, 403
    
    isOk = proxmox.check_dns_ip_entry(user_id, body.ip)
    if isOk is None :
        return {"error": "An error occured while checking your ip addresses. Please try again."}, 500
    elif not isOk and not admin:
        return {"error": "This ip address isn't associated to one of your vms. This is illegal. This incident will be reported."}, 403
    elif admin : 
        vmWithIp = get_vm_from_ip(body.ip)
        if vmWithIp is None :
            return {"error": "This ip address isn't associated to one vms."}, 400
        print(vmWithIp)
        user_id = vmWithIp.userId
    return proxmox.add_user_dns(user_id, body.entry, body.ip)


def create_vm(body=None):  # noqa: E501
    """create vm

     # noqa: E501

    :param body: VM to create
    :type body: dict | bytes

    :rtype: None
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"error": "Your are not allowed to be here"}, 403

    user_id = cas['sub']
    
    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;
    if admin:
        freezeAccountState = 0
    else:    
        user_id = cas['sub']
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState != 0 and not admin: # for any other freestate user can't create vm
        return {"error": "Your cotisation has expired"}, 403
    if connexion.request.is_json:
        body = VmItem.from_dict(connexion.request.get_json())  # noqa: E501
    try :
        if body.cpu == 0 or body.ram == 0 or body.disk == 0 or body.cpu is None or body.ram is None or body.disk is None:
            return {"error": "Impossible to create a VM without CPU, RAM or disk"}, 400
    except Exception as e:
        return {"error": "Impossible to create a VM without CPU, RAM or disk. No data transmitted"}, 400
    
    alreadyUsedCPU = 0
    alreadyUsedRAM = 0
    alreadyUsedDisk = 0
    userVms, status = proxmox.get_vm(user_id=user_id)
    if status != 200:
        return {"error": "Error while getting your other VMs"}, 500
    for vmid in userVms:
        node, status = proxmox.get_node_from_vm(vmid)
        if status != 200:
            return {"error": "Error while getting your other VMs ressources"}, 500
        vm, status = proxmox.get_vm_config(vmid, node)
        if status != 201:
            return vm, status
        alreadyUsedCPU += int(vm["cpu"])
        alreadyUsedRAM += int(vm["ram"])
        alreadyUsedDisk += int(vm["disk"])
    account_ressources = dbfct.get_vm_max_ressources();

    if account_ressources is None:
        return {"error": "Error while getting ressources default"}, 500
   
    if alreadyUsedCPU + body.cpu > account_ressources["cpu_max"] or alreadyUsedRAM + body.ram > account_ressources["ram_max"] or alreadyUsedDisk + body.disk > account_ressources["storage_max"]:
        return {"error": "You have already used all your resources"}, 403
    if body.name is None or body.type is None or body.password is None or body.user is None or body.ssh_key is None:
        return {"error": "You have to fill all the fields"}, 400
    return proxmox.create_vm(body.name, body.type, user_id, body.cpu, body.ram, body.disk, body.password, body.user, body.ssh_key, )

def delete_vm_id_with_error(vmid): #API endpoint to delete a VM when an error occured
    """delete vm by id where an error occured

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
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;

    user_id = cas['sub']
    if not admin and dbfct.get_vm_userid(vmid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500

    if freezeAccountState >= 3 and not admin:
        return {"error": "cotisation expired"}, 403

    if not vmid in map(int, proxmox.get_vm(user_id)[0]) and not admin:
        return {"error": "You don't have the right permissions"}, 403
    
    Thread(target=delete_vm_in_thread, args=(vmid, user_id, "", True,)).start()
    return {"status": "deleting"}, 200

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
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;

    user_id = cas['sub']
    if not admin and dbfct.get_vm_userid(vmid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # if freeze state 1 or 2 user still have access to proxmox
        return {"status": "cotisation expired"}, 403
    
    node,status = proxmox.get_node_from_vm(vmid)
    if status != 200 : #doesn't exist
        return {"error": "VM doesn't exist"}, 404
    
    Thread(target=delete_vm_in_thread, args=(vmid, user_id, node,False,)).start()
    return {"status": "deleting"}, 200


# Delete the vm in a thread after the API endpoint is called. It's a workaround to avoid the timeout of the API endpoint. The behavior is different in the error handling if the deletion is trigger while an error or not
def delete_vm_in_thread(vmid, user_id, node="", dueToError=False):
    print("Deleting VM " + str(vmid) + ". Is due to an error :", dueToError)
    util.update_vm_state(vmid, "deleting")
    try :
        if node == "" and not dueToError:
            print("Impossible to find the vm to delete.")
            util.update_vm_state(vmid, "Impossible to find the vm to delete.", errorCode=404, deleteEntry=True)
            return 0
        elif node != "" : 
            isProxmoxDeleted = proxmox.delete_from_proxmox(vmid, node)
            print("isProxmoxDeleted : " + str(isProxmoxDeleted))
            if not isProxmoxDeleted and not dueToError:
                print("An error occured while deleting the VM from proxmox")
                util.update_vm_state(vmid, "An error occured while deleting the VM from proxmox", errorCode=500, deleteEntry=True)
                return 0
            # If not isProxmoxDeleted and dueToError then it's fine. 
        # Now we can delete the entry in the db
        isDNSDeleted = proxmox.delete_from_dns(vmid)
        if not isDNSDeleted and not dueToError:
            print("An error occured while deleting the DNS entry")
            util.update_vm_state(vmid, "An error occured while deleting the DNS entry", errorCode=500, deleteEntry=True)
            return 0
        isDbDeleted = proxmox.delete_from_db(vmid)
        if (not dueToError and isDbDeleted and isProxmoxDeleted) or (dueToError and (isDbDeleted or not isProxmoxDeleted)):
            util.update_vm_state(vmid, "deleted", deleteEntry=True)
            return 1
        else : 
            print("An error occured while deleting the VM.")
            util.update_vm_state(vmid, "An error occured while deleting the VM.", errorCode=500, deleteEntry=True)
    except Exception as e:
        print("An error occured while deleting the VM. Exception : " + str(e))
        util.update_vm_state(vmid, "An error occured while deleting the VM. Exception : " + str(e), errorCode=500, deleteEntry=True)

    node,status = proxmox.get_node_from_vm(vmid)
    if status != 200: 
        return {"status": "vm not exists"}, 404
    if vmid in map(int, proxmox.get_vm(user_id)[0]):
        return proxmox.delete_vm(vmid, node)
    else:
        return {"status": "error"}, 500


def get_dns():  # noqa: E501
    """check if a user has signed the hosting charter

     # noqa: E501


    :rtype: List[DnsEntryItem]
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;
    user_id = cas['sub']
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 and 2, the user still can be connected to hosting
        return {"status": "cotisation expired"}, 403

   

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                return proxmox.get_user_dns()

    return proxmox.get_user_dns(user_id)

# /vms
def get_vm(search= ""):  # noqa: E501
    """get all user vms

     # noqa: E501

    :rtype: List[VmIdItem]
    """
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"status": "error"}, 403
    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;

    user_id = cas['sub']
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"error": "cotisation expired"}, 403


    

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                return proxmox.get_vm(search=search)  # affichage de la liste sans condition
 
    return proxmox.get_vm(user_id=user_id)

# /vm/{vmid}
def get_vm_id(vmid):  # noqa: E501
    """get a vm by id

     # noqa: E501

    :param vmid: vmid to get
    :type vmid: string

    :rtype: VmItem
    """


    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"error": "Impossible to check your account. Please log into the MiNET cas"}, 403
    
    admin = False

    try:
        vmid = int(vmid)
    except:
        return {"error": "The request contains errors"}, 400

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    user_id = cas['sub']
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
   
   
    if freezeAccountState >= 3: # For freeze state 1 or 2, the user can access to hosting
        return {"error": "cotisation expired"}, 403

    

    
    vm_state = util.get_vm_state(vmid)
    if vm_state != None : # if not then the vm is created of not found. Before get the proxmox config, we must be sure the vm is not creating or deleting
        
        (status, httpErrorCode, errorMessage) = vm_state 
        if status == "error":
            util.update_vm_state(vmid, "delete", deleteEntry= True) # We send to the user and delete here
            try : 
                return {"error": errorMessage}, int(httpErrorCode)
            except: 
                return {"error":  "An unknown error occured"}, 500
        elif not vmid in map(int, proxmox.get_vm(user_id)[0]) and not admin: # we authorize to consult error message
            return {"error": "You don't have the right permissions"}, 403
        elif status == "creating" : 
            return {"status" : "creating"}, 200
        elif status == "deleting":
            return {"status" : "deleting"}, 200
        elif status == "deleted":
            util.update_vm_state(vmid, "deleted", deleteEntry= True) # We send to the user and delete here
            return {"status": "deleted"}, 200
        elif  status == "created" : 
            util.update_vm_state(vmid, "delete", deleteEntry= True) # We send to the user and delete here
            return {"status": "created"}, 201
        else :
            return {"error": "Unknown vm status"}, 400
    
    node,status = proxmox.get_node_from_vm(vmid)
    

    if not admin and dbfct.get_vm_userid(vmid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    elif status != 200 and not admin: # exist in the db but not in proxmox. It's a error
        return {"error": "VM not found in proxmox"}, 500
    elif status != 200 and  admin:
        return {'error' : "VM no found"} , 404



    status = proxmox.get_proxmox_vm_status(vmid, node)
    type = dbfct.get_vm_type(vmid)
    created_on = get_vm_created_on(vmid)
   
    (vmConfig, response) = proxmox.get_vm_config(vmid, node)
    #print("get_vm_config for " , vmid , " took ")


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
    
    try:
        vm = get_vm_db_info(vmid)
        isUnsecure = vm.unsecure
    except:
        isUnsecure = None

   # print("recieved config response (" ,vmid ,") ok. Took" , str(time.time() - start))

    owner = get_vm_userid(vmid)  # on renvoie l'owner pour que les admins puissent savoir à quel user appartient quelle vm

    if status[0]["status"] != 'running':
        return {"name": name, "autoreboot": autoreboot, "user": owner if admin else "", "ip": "", "status": status[0]["status"],
                "ram": ram, "cpu": cpu, "disk": disk, "type": type[0]["type"],
                "ram_usage": 0, "cpu_usage": 0, "uptime": 0, "created_on": created_on[0]["created_on"], "unsecure" : isUnsecure}, 201
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
    ipAddr = ""
    if ip[1] == 200 or ip[1] == 201:
       ipAddr = ip[0]["vm_ip"]
    if  (status[1] == 201 or status[1] == 200) and (type[1] == 201 or type[1] == 200) :
        return {"name": name, "autoreboot": autoreboot, "user": owner if admin else "", "ip": ipAddr
                   , "status": status[0]["status"], "ram": ram
                   , "cpu": cpu, "disk": disk, "type": type[0]["type"]
                   , "ram_usage": ram_usage, "cpu_usage": cpu_usage
                   , "uptime": uptime, "created_on": created_on[0]["created_on"], "unsecure":isUnsecure}, 201

    elif   status[1] == 404 or type[1] == 404  :
        return {"error": "vm not found"}, 404
    else :
        print("datal error for vm ", vmid, "Unknown error one of the status, type or ip doesn't exists : ", status, type, ip)
        return {"error": "Unknown error one of the status, type or ip doesn't exists."}, 500


def renew_ip():
    if connexion.request.is_json:
        body = connexion.request.get_json()  # noqa: E50

    try:
        vmid = int(body['vmid'])
    except:
        return {"error": "Bad vmid"}, 400
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;

    user_id = cas['sub']
    if not admin and dbfct.get_vm_userid(vmid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    if admin :
        freezeAccountState = 0 # Un admin n'a pas d'expiration de compte
    else :
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
    
    if freezeAccountState >= 3: # if freeze state 1 or 2 the user can access to proxmox
        return {"status": "cotisation expired"}, 403
    if not vmid in map(int, proxmox.get_vm(user_id)[0]) and not admin:
        return {"error": "You don't have the right permissions"}, 403

    return proxmox.renew_ip(vmid)



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
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;
    user_id = cas['sub']
    if not admin and dbfct.get_entry_userid(dnsid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
   
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"status": "cotisation expired"}, 403

    user_id = cas['sub']

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
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
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True;
    user_id = cas['sub']
    if not admin and dbfct.get_entry_userid(dnsid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"status": "cotisation expired"}, 403

    user_id = cas['sub']

    try:
        dnsid = int(dnsid)
    except:
        return {"status": "error not an integer"}, 500

    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
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
        requetsBody = VmItem.from_dict(connexion.request.get_json())  # noqa: E501
    try:
        vmid = int(vmid)
    except:
        return {"status": "error not an integer"}, 500

    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"status": "error"}, 403

    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    user_id = cas['sub']
    if not admin and dbfct.get_vm_userid(vmid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    if admin: 
        freezeAccountState = 0
    else: 
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
   
    if freezeAccountState >= 3 and not admin: # For freeze state 1 or 2, the user can access to hosting
        return {"status": "cotisation expired"}, 403

    user_id = cas['sub']

    if admin or dbfct.get_vm_userid(vmid) == user_id : # if not admin, we check if the user is the owner of the vm
        node,status = proxmox.get_node_from_vm(vmid)
        if status != 200:
            return {"status": "vm not exists"}, 404
        if requetsBody.status == "start":
            return proxmox.start_vm(vmid, node)
        if requetsBody.status == "reboot":
            return proxmox.reboot_vm(vmid, node)
        elif requetsBody.status == "stop":
            return proxmox.stop_vm(vmid, node)
        elif requetsBody.status == "switch_autoreboot":
            return proxmox.switch_autoreboot(vmid, node)
        elif requetsBody.status == "transfering_ownership":
            if admin : 
                new_owner = requetsBody.user
                return proxmox.transfer_ownership(vmid, new_owner)
            else: 
                return {"status": "Permission denied"}, 403
        else:
            return {"status": "uknown status"}, 500
    else:
        return {"status": "Permission denied"}, 403

def get_historyip(vmid):
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"status": "error"}, 403

    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    if admin == True:
        return get_historyip_fromdb(vmid)
    else:
        return {"status": "error"}, 403

def get_historyipall():
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"status": "error"}, 403

    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True

    if admin == True:
        return get_historyip_fromdb()
    else:
        return {"status": "error"}, 403


# Return the list of all ips of a user

def get_ip_list():
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"status": "This is forbidden"}, 403
    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True
    user_id = cas['sub']
    if admin :
        freezeAccountState = 0 # Un admin n'a pas d'expiration de compte
    else :
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
    
    if freezeAccountState >= 3: # if freeze state 1 or 2 the user can access to proxmox
        return {"status": "cotisation expired"}, 403

    list = proxmox.get_user_ip_list(cas["id"])
    if list == None:
        return {"status": "Impossible to retrieve the list of your ip addresses. Please make juste you have at least one."}, 500
    else : 
        return {"ip_list": list}, 200

def update_credentials():

    if connexion.request.is_json:
        update_body = connexion.request.get_json()  # noqa: E50

    try:
        vmid = int(update_body['vmid'])
    except:
        return {"error": "Bad vmid"}, 400
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)

    if status_code != 200:
        return {"status": "error"}, 403

    admin = False
    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):
                admin = True

    user_id = cas['sub']
    if not admin and dbfct.get_vm_userid(vmid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'status' : "Forbidden"} , 403
    if admin :
        freezeAccountState = 0 # Un admin n'a pas d'expiration de compte
    else :
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"status": "error while getting freeze state"}, 500
    
    if freezeAccountState >= 3: # if freeze state 1 or 2 the user can access to proxmox
        return {"status": "cotisation expired"}, 403
    if not vmid in map(int, proxmox.get_vm(user_id)[0]) and not admin:
        return {"status": "You don't have the right permissions"}, 403
    print("body =", update_body)
    if not "password" in update_body or not "sshKey" in update_body or not "username" in update_body:
        return {"status" : "Missing parameters. You must provide a username, a password and a valid public ssh key"}, 400

    

    if not util.check_password_strength(update_body['password']):
        return {"status" : "Incorrect password format. Your password must contain at least 1 special char, 1 uppercase letter, 1 number and 8 chars in total."}, 400
    if not util.check_ssh_key(update_body['sshKey']):
        return {"status" : "Incorrect ssh key format"}, 400
    if not util.check_username(update_body['username']):
        return {"status" : "Incorrect vm user format"}, 400
    
    return proxmox.update_vm_credentials(vmid, update_body['username'], update_body['password'], update_body['sshKey'])

    

def get_need_to_be_restored(vmid):
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    
    if status_code != 200:
        return {"error": "Impossible to check your account. Please log into the MiNET cas"}, 403

    user_id = cas['sub']
    admin = False
    
    try:
        vmid = int(vmid)
    except:
        return {"error": "The request contains errors"}, 400

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True
    if not admin and dbfct.get_vm_userid(vmid) != user_id : # if not admin, we check if the user is the owner of the vm
        return {'error' : "Forbidden"} , 403
    if admin :
        freezeAccountState = 0 # Un admin n'a pas d'expiration de compte
    else :
        body,statusCode = proxmox.get_freeze_state(user_id)
        if statusCode != 200:
            return body, statusCode
        try:
            freezeAccountState = int(body["freezeState"])
        except Exception as e:
            return {"error": "error while getting freeze state"}, 500
    
    if freezeAccountState >= 3: # if freeze state 1 or 2 the user can access to proxmox
        return {"status": "cotisation expired"}, 403

    if not vmid in map(int, proxmox.get_vm(user_id)[0]) and not admin:
        return {"error": "You don't have the right permissions"}, 403


    
    try : 
        value =  dbfct.getNeedToBeRestored(vmid)
        return {"need_to_be_restored": value}, 200
    except :
        return {"error": "Impossible to check the restore status of the vm"}, 500
    



def get_account_state(username):
    headers = connexion.request.headers
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"error": "Impossible to check your account. Please log into the MiNET cas"}, 403

    user_id = cas['sub']
    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True
    if admin and user_id.lower() == username.lower(): 
        return {"freezeState" : "0"}, 200 # we fake it
    elif admin or user_id.lower() == username.lower():
        return proxmox.get_freeze_state(username)
    else :
        return {"error": "You are not allowed to check this account"}, 403



def get_notification():
    headers = connexion.request.headers
    try:
        status_code, cas = util.check_cas_token(headers)
        if status_code != 200:
            return {"error": "Impossible to check your account. Please log into the MiNET cas"}, 403

        admin = False

        if "attributes" in cas:
            if "memberOf" in cas["attributes"]:
                if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                    admin = True
    except:
        admin = False

    
    notif = dbfct.get_notification()
    if admin or notif != None:
        return notif, 200
    else:
        return {}, 204 # no content


def put_notification():
    headers = connexion.request.headers
    status_code, cas = util.check_cas_token(headers)
    print("cas", cas)
    if status_code != 200:
        return {"error": "Impossible to check your account. Please log into the MiNET cas"}, 403

    admin = False

    if "attributes" in cas:
        if "memberOf" in cas["attributes"]:
            if is_admin(cas["attributes"]["memberOf"]):  # partie admin pour renvoyer l'owner en plus
                admin = True
    
    if not admin:
        return {"error": "You are not allowed to do this"}, 403
    try:
        title = connexion.request.json.get("title")
        message = connexion.request.json.get("message")
        criticity = connexion.request.json.get("criticity")
        active = connexion.request.json.get("active")
        if title == None or message == None or criticity == None or active == None:
            return {"error": "Missing parameters"}, 400
    except Exception as _:
        return {"error": "Missing parameters"}, 400
    dbfct.put_notification(title, message, criticity, active)
    return {}, 201


def get_account_max_ressources():
    headers = {"Authorization": connexion.request.headers["Authorization"]}
    status_code, cas = util.check_cas_token(headers)
    if status_code != 200:
        return {"status": "error"}, 403
    
    return get_vm_max_ressources(), 200