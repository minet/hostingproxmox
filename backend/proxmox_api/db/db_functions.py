from proxmox_api.db.db_models import *
import proxmox_api.config.configuration as config
import time
import threading


#####DB


def update_vm_ip(vmid, vmip):

    vm = Vm.query.filter_by(id=vmid).first()
    vm.ip = vmip
    db.session.commit()


def get_vm_db_info(vmid):
    return  Vm.query.filter_by(id=vmid).first()

def get_user_id(user_id):
    return User.query.filter_by(id=user_id).first()


def get_vm_list(user_id=""):  # user id est vide quand un admin veut voir la liste
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


def add_user(user):
    new_user = User(id=user)
    db.session.add(new_user)
    db.session.commit()


def add_vm(id, user_id, type, mac, ip):
    new_vm = Vm(id=id, userId=user_id, type=type, mac=mac, ip=ip)
    db.session.add(new_vm)
    db.session.commit()


def del_vm_list(del_vmid):
    print("del vm list")
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

def get_historyip_fromdb(vmid = ""): # vmid vide si on récupère tt l'historique
    list = []
    if vmid != "":
        for i in History.query.filter_by(vmId=vmid).all():
            list.append([i.ip,i.date,i.userId,i.vmId])
    else:
        for i in History.query.all():
            list.append([i.ip,i.date,i.userId,i.vmId])
    return list

def is_ip_available(ip): #permet de définir si l'ip est disponible... ou non
    if Vm.query.filter_by(ip=ip).first():
        return False
    else:
        return True;


def get_active_users(): # return actives users (ie those who have a vm)
    list = []
    for vm in Vm.query.all():
        if vm.userId:
            list.append(vm.userId)
    return list


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
    #print("update last botif date", user, username, date)
    db.session.commit()


#######
