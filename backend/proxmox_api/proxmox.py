import random
import urllib.parse
from time import sleep

from proxmoxer import ProxmoxAPI
from proxmoxer import ResourceException
import proxmox_api.ddns as ddns
from proxmox_api.config import configuration as config
from proxmox_api.db.db_functions import *

proxmox = ProxmoxAPI(host=config.PROXMOX_HOST, user=config.PROXMOX_USER
                     , token_name=config.PROXMOX_API_KEY_NAME
                     , token_value=config.PROXMOX_API_KEY, verify_ssl=False)


def add_user_dns(user_id, entry, ip):
    rep_msg, rep_code = ddns.create_entry(entry, ip)
    if rep_code == 201:
        add_dns_entry(user_id, entry, ip)
    return rep_msg, rep_code


def get_user_dns(user_id):
    try:
        dnsList = get_dns_entries(user_id)
        return dnsList, 201
    except:
        return {"dns": "error occured"}, 500


def del_user_dns(dnsid):
    entry = get_entry_host(dnsid)[0]['host']
    if entry is None:
        return {"dns": "not found"}, 404
    ddns_rep = ddns.delete_dns_record(entry)
    if ddns_rep[1] == 201:
        del_dns_entry(dnsid)
    return ddns_rep


def random_server():
    node_number = len(proxmox.nodes.get())
    return proxmox.nodes.get()[random.randint(0, node_number - 1)]['node']


def delete_vm(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm['vmid'] == vmid:

            try:
                if get_vm_status(vmid)[0]['status'] == 'stopped':
                    print("Del VM")
                    proxmox.nodes(vm["node"]).qemu(vmid).delete()
                    print("VM deleted")
                    print("Updating user")
                    del_vm_list(vmid)
                    print("User updated")
                    return {"state": "vm deleted"}, 201
                else:
                    print("Stopping vm")
                    stop_vm(vmid)
                    while get_vm_status(vmid)[0]['status'] != 'stopped':
                        sleep(1)
                    print("Vm stopped")
                    print("Del VM")
                    proxmox.nodes(vm["node"]).qemu(vmid).delete()
                    print("VM deleted")
                    print("Updating user")
                    del_vm_list(vmid)
                    print("User updated")
                    return {"state": "vm deleted"}, 201
            except:
                print("ERREUR")
                return {"state": "error"}, 500
    return {"state": "vm not found"}, 404


def create_vm(name, vm_type, user_id, password="no", vm_user="no", main_ssh_key="no"):
    next_vmid = int(proxmox.cluster.nextid.get())
    server = random_server()

    try:
        if vm_type == "bare_vm":
            proxmox.nodes(server).qemu(10000).clone.create(
                name=name,
                newid=next_vmid
            )
        elif vm_type == "nginx_vm":
            proxmox.nodes(server).qemu(10001).clone.create(
                name=name,
                newid=next_vmid
            )
        else:
            return {"status": "vm type not defines"}, 500

        user = get_user_id(user_id=user_id)
        print("Selecting user")
        if user is None:
            add_user(user_id)
            add_vm(id=next_vmid, user_id=user_id, type=vm_type)
        else:
            add_vm(id=next_vmid, user_id=user_id, type=vm_type)
        print("User selected")
    except:
        print("erreur lors de la création")
        delete_vm(next_vmid)
        return {"status": "error"}, 500

    if password != "no":
        print("Setting password")
        try:
            proxmox.nodes(server).qemu(next_vmid).config.create(
                cipassword=password
            )
        except:
            print("ERREUR")
            delete_vm(next_vmid)
            return {"status": "error"}, 500
        print("Password set")

    if vm_user != "no":
        print("Setting user")
        try:
            proxmox.nodes(server).qemu(next_vmid).config.create(
                ciuser=vm_user
            )
        except:
            print("ERREUR")
            delete_vm(next_vmid)
            return {"status": "error"}, 500
        print("user set")

    if main_ssh_key != "no":
        print("Setting ssh")
        try:
            print(main_ssh_key)
            proxmox.nodes(server).qemu(next_vmid).config.create(
                sshkeys=urllib.parse.quote(main_ssh_key, safe='')
            )
        except:
            delete_vm(next_vmid)
            print("ERREUR SSH")
            return {"status": "error"}, 500
        print("ssh set")

    try:
        proxmox.nodes(server).qemu(next_vmid).status.start.create()

    except:
        print("ERREUR")
        delete_vm(next_vmid)
        return {"status": "error"}, 500
    return {"status": "Vm created"}, 201


def start_vm(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                proxmox.nodes(vm["node"]).qemu(vmid).status.start.create()
                return {"state": "vm started"}, 201
            except:
                print("ERREUR")
                return {"status": "error"}, 500
    return {"state": "vm not found"}, 404


def stop_vm(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                if get_vm_status(vmid)[0]['status'] != 'stopped':
                    proxmox.nodes(vm["node"]).qemu(vmid).status.stop.create()
                    return {"state": "vm stopped"}, 201
                else:
                    return {"state": "vm already stopped"}, 201
            except:
                print("ERREUR")
                return {"state": "error"}, 500
    return {"state": "vm not found"}, 404


def get_vm_ip(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                ips = []
                for int in proxmox.nodes(vm["node"]).qemu(vmid).agent.get("network-get-interfaces")['result']:
                    print(int['name'])
                    if int['name'] != 'lo':
                        for ip in int['ip-addresses']:
                            if ip['ip-address-type'] == "ipv4":
                                ips.append(ip["ip-address"])

                return {"vm_ip": ips}, 201
            except:
                print("ERREUR")
                return {"vm_ip": "error"}, 500
    return {"vm_ip": "Vm not found"}, 404


def get_vm_name(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                name = proxmox.nodes(vm["node"]).qemu(vmid).config.get()['name']
                return {"name": name}, 201
            except:
                print("ERREUR")
                return {"name": "error"}, 500
    return {"name": "Vm not found"}, 404


def get_vm(user_id):
    return get_vm_list(user_id), 201


def get_vm_cpu(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                cpu = proxmox.nodes(vm["node"]).qemu(vmid).config.get()['sockets'] * \
                      proxmox.nodes(vm["node"]).qemu(vmid).config.get()['cores']
                return {"cpu": cpu}, 201
            except:
                print("ERREUR")
                return {"cpu": "error"}, 500
    return {"cpu": "Vm not found"}, 404


def get_vm_disk(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                disk = int(proxmox.nodes(vm["node"]).qemu(vmid).config.get()['scsi0'].split('=')[-1].replace('G', ''))
                return {"disk": disk}, 201
            except:
                print("ERREUR")
                return {"disk": "error"}, 500
    return {"disk": "Vm not found"}, 404


def get_vm_ram(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                ram = proxmox.nodes(vm["node"]).qemu(vmid).config.get()['memory']
                return {"ram": ram}, 201
            except:
                print("ERREUR")
                return {"ram": "error"}, 500
    return {"ram": "Vm not found"}, 404


def get_vm_status(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            qemu_status = proxmox.nodes(vm["node"]).qemu(vmid).status.current.get()['status']
            try:
                qemu_agent_status = proxmox.nodes(vm["node"]).qemu(vmid).agent.ping.create()

                if qemu_agent_status:
                    qemu_agent_status = True
                else:
                    qemu_agent_status = False

                if (qemu_status == 'running') & qemu_agent_status:
                    return {"status": "running"}, 201
                elif (qemu_status == 'running') & (not qemu_agent_status):
                    return {"status": "booting"}, 201
                else:
                    return {"status": "stopped"}, 201


            except ResourceException:  # qemu_agent error
                if qemu_status == 'running':
                    return {"status": "booting"}, 201

                else:
                    return {"status": "stopped"}, 201

            except:
                print("Erreur")
                return {"status": "error"}, 500

    return {"status": "vm not found"}, 404
