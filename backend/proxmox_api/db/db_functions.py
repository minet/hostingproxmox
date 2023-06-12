from proxmox_api.db.db_models import *
import proxmox_api.config.configuration as config
import time
import threading

###################
####### VM ########
###################


def update_vm_ip(vmid, vmip):

    vm = Vm.query.filter_by(id=vmid).first()
    vm.ip = vmip
    
    db.session.commit()


def get_vm_ip(vmid):
    vm = Vm.query.filter_by(id=vmid).first()
    return vm.ip


def update_vm_mac(vmid, mac):

    vm = Vm.query.filter_by(id=vmid).first()
    vm.mac = mac
    db.session.commit()


def get_vm_db_info(vmid):
    return  Vm.query.filter_by(id=vmid).first()


def update_vm_userid(vmid, userid):
    vm = Vm.query.filter_by(id=vmid).first()
    vm.userId = userid
    db.session.commit()

# Retrieve the VM from the DB using the IP
def get_vm_from_ip(ip):
    return Vm.query.filter_by(ip=ip).first()



def add_vm(id, user_id, type, mac, ip):
    new_vm = Vm(id=id, userId=user_id, type=type, mac=mac, ip=ip)
    db.session.add(new_vm)
    db.session.commit()


def del_vm_list(del_vmid):
    Vm.query.filter_by(id=del_vmid).delete()
    db.session.commit()


def get_vm_userid(vmid):
    userid = Vm.query.filter_by(id=vmid).first().userId
    return userid


def get_vm_type(vmid):
    type = Vm.query.filter_by(id=vmid).first().type

    if type is not None:
        return {"type": type}, 201
    else:
        return {"type": "vm not found"}, 404

def get_vm_created_on(vmid):
    created_on = Vm.query.filter_by(id=vmid).first().created_on

    if created_on is not None:
        return {"created_on": created_on}, 201
    else:
        return {"created_on": "vm not found"}, 404

def is_ip_available(ip): #permet de définir si l'ip est disponible... ou non
    if Vm.query.filter_by(ip=ip).first():
        return False
    else:
        return True;

def getNextVmID(min = 110): # get the next vmid available. The minimum whould not be less than 110
    if min <110 : 
        min = 110
    for vmid in (range(min, 999)): # should not exceed 999, if not, we have a problem
        if Vm.query.filter_by(id=vmid).first() is None:
            return vmid 

def getNeedToBeRestored(vmid):
    return Vm.query.filter_by(id=vmid).first().needToBeRestored

def setNeedToBeRestored(vmid, needToBeRestored):
    vm = Vm.query.filter_by(id=vmid).first()
    vm.needToBeRestored = needToBeRestored
    db.session.commit()

def get_vm_status(vmid): # Return the status of the VM and if there is an error (statusMessae (str), isError (bool)
    vm = Vm.query.filter_by(id=vmid).first()
    if vm == None:
        return "deleted", False
    status = vm.status
    if status is None:
        return "created", False
    if "error" in status:
        try : 
            status = status.split(":")[1]
            return status, True
        except:
            return "Unknown error", True
    else :
        print('status', status)
        return status, False

def set_vm_status(vmid, status, isAnError=False):
    print('set status', status)
    if isAnError:
        status = "error: " + status
    vm = Vm.query.filter_by(id=vmid).first()
    if vm is None:
        return None
    vm.status = status
    db.session.commit()

###################
###### USER #######
###################

def get_user_list(user_id=None, searchItem = None): # filter is for the user name
    if user_id is not None:
        return User.query.filter_by(id=user_id).first()
    elif searchItem is not None:
        search = "%{}%".format(searchItem)
        start = time.time()
        filtered = User.query.filter(User.id.like(search)).all()
        return filtered
        
    else : 
        return User.query.all()

# Return all the VM of an user
def get_vm_list(user_id=""): 
    if user_id != "":  # dans ce cas on affiche ce qui est lié à l'user
        if User.query.filter_by(id=user_id).first() is None:
            return []
        else:
            list = []
            for vm in User.query.filter_by(id=user_id).first().vms:
                list.append(vm.id)
            return list
    else:  # dans ce cas on affiche touuute la liste sans restriction
        list = []
        for i in User.query.all():
            for j in i.vms:
                    list.append(j.id)
        return list



def add_user(user):
    new_user = User(id=user)
    db.session.add(new_user)
    db.session.commit()

def updateFreezeState(username, freezeState):
    user = User.query.filter_by(id=username).first()
    user.freezeState = freezeState
    #print("update freeze state", user, username, freezeState)
    db.session.commit()

def getFreezeState(username):
    user = User.query.filter_by(id=username).first()
    if user is None:
        print("user not found", username)
        return None
    return user.freezeState

def getLastNotificationDate(username):
    user = User.query.filter_by(id=username).first()
    if user is None:
        print("user not found", username)
        return None
    return user.lastNotificationDate


def updateLastNotificationDate(username, date):
    user = User.query.filter_by(id=username).first()
    user.lastNotificationDate = date
    db.session.commit()


# Return expired users with a freezeState >= minimumFreezeState
def get_expired_users(minimumFreezeState = 1):
    list = []
    for user in User.query.all():
        if user.freezeState !=None:
            state = user.freezeState.split(".")[0]
            if int(state) >= minimumFreezeState:
                list.append(user.id)
    return list

def ban_user(username):
    user = User.query.filter_by(id=username).first()
    user.isBanned = True
    db.session.commit()

def unban_user(username):
    user = User.query.filter_by(id=username).first()
    user.isBanned = False
    db.session.commit()


###################
###### DNS ########
###################

# Retrieve all dns entries from the DB using an IP
def get_dns_entry_from_ip(ip):
    list = []
    for dn in DomainName.query.all():
        if dn.ip == ip:
            list.append(dn.id)
    return list


def add_dns_entry(user, entry, ip):
    new_entry = DomainName(userId=user, entry=entry, ip=ip)
    db.session.add(new_entry)
    db.session.commit()

def del_dns_entry(dnsid):
    DomainName.query.filter_by(id=dnsid).delete()
    db.session.commit()


def get_dns_entries(user_id=""):  # user_id vide quand un admin se connecte
    if user_id != "":
        if User.query.filter_by(id=user_id).first() is None:
            return []
        else:
            list = []
            DnsList = User.query.filter_by(id=user_id).first().dnsEntries
            for i in DnsList:
                list.append(i.id)
            return list
    else:
        list = []
        for i in User.query.all():
            for j in i.dnsEntries:
                list.append(j.id)
        return list


def get_entry_ip(id):
    ip = DomainName.query.filter_by(id=id).first().ip
    return {"ip": ip}, 201

    # if ip is None:
    #   return {"dns": "not found"}, 404
    # else:
    #   return {"ip": ip}, 201


def get_entry_host(id):
    host = DomainName.query.filter_by(id=id).first().entry
    if host is None:
        return {"dns": "not found"}, 404
    else:
        return {"host": host}, 201


def get_entry_userid(dnsid):
    userid = DomainName.query.filter_by(id=dnsid).first().userId
    return userid


# Update all the dns records owner for an ip
def update_all_ip_dns_record(ip, new_owner):
    for dns in DomainName.query.filter_by(ip=ip).all():
        dns.userId = new_owner
        db.session.commit()

# delete all the dns records for an ip
def delete_ip_dns_record(ip):
    DomainName.query.filter_by(ip=ip).delete()
    db.session.commit()
###################
##### HISTORY #####
###################

def get_historyip_fromdb(vmid = ""): # vmid vide si on récupère tt l'historique
    list = []
    if vmid != "":
        for i in History.query.filter_by(vmId=vmid).all():
            list.append([i.ip,i.date,i.userId,i.vmId])
    else:
        for i in History.query.all():
            list.append([i.ip,i.date,i.userId,i.vmId])
    return list
    
def add_ip_to_history(ip, vmid, userid):
    new_ip = History(ip=ip, vmId=vmid, userId=userid)
    db.session.add(new_ip)
    db.session.commit()


###################
## NOTIFICATION ###
###################

def get_notification():
    notif = Notification.query.first()
    if notif is not None:
        return {"title": notif.title, "message": notif.message, "criticity": notif.criticity, "active": notif.active}
    return None

def put_notification(title, message,criticity, active):
    notif = Notification.query.first()
    if notif is None:
        new_notif = Notification(title=title, message=message, criticity=criticity, active=active)
        db.session.add(new_notif)
        db.session.commit()
    else:
        notif.title = title
        notif.message = message
        notif.criticity = criticity
        notif.active = active
        db.session.commit()



#####################
### VM_RESSOURCES ###
#####################

def get_vm_max_ressources():
    ressources = Account_Max_Ressources.query.all()
    account_ressources = {}
    if ressources is not None:
        for ressource in ressources:
            if ressource.id == "cpu":
                account_ressources["cpu_max"] = ressource.ressources
            elif ressource.id == "ram":
                account_ressources["ram_max"] = ressource.ressources
            elif ressource.id == "storage":
                account_ressources["storage_max"] = ressource.ressources
        return account_ressources
    return None