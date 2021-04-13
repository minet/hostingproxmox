from proxmox_api.db.db_models import *


#####DB
def get_user_id(user_id):
    return User.query.filter_by(id=user_id).first()


def get_vm_list(user_id = ""): # user id est vide quand un admin veut voir la liste
    if user_id != "": # dans ce cas on affiche ce qui est lié à l'user
        if User.query.filter_by(id=user_id).first() is None:
            return []
        else:
            list = []
            for i in User.query.filter_by(id=user_id).first().vms:
                list.append(i.id)
            return list
    else: # dans ce cas on affiche touuute la liste sans restriction
        list = []
        for i in User.query.vms:
            list.append(i.id)
        return list



def add_dns_entry(user, entry, ip):
    new_entry = DomainName(userId=user, entry=entry, ip=ip)
    db.session.add(new_entry)
    db.session.commit()


def del_dns_entry(dnsid):
    DomainName.query.filter_by(id=dnsid).delete()
    db.session.commit()


def get_dns_entries(user_id):
    if User.query.filter_by(id=user_id).first() is None:
        return []
    else:
        list = []
        DnsList = User.query.filter_by(id=user_id).first().dnsEntries
        for i in DnsList:
            list.append(i.id)
        return list


def get_entry_ip(id):
    ip = DomainName.query.filter_by(id=id).first().ip
    return {"ip": ip}, 201

    #if ip is None:
     #   return {"dns": "not found"}, 404
    #else:
     #   return {"ip": ip}, 201


def get_entry_host(id):
    host = DomainName.query.filter_by(id=id).first().entry
    if host is None:
        return {"dns": "not found"}, 404
    else:
        return {"host": host}, 201


def add_user(user):
    new_user = User(id=user)
    db.session.add(new_user)
    db.session.commit()


def add_vm(id, user_id, type):
    new_vm = Vm(id=id, userId=user_id, type=type)
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

#######
