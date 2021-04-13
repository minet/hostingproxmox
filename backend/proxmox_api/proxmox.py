import random
import urllib.parse
from time import sleep
import logging
from proxmoxer import ProxmoxAPI
from proxmoxer import ResourceException
import proxmox_api.ddns as ddns
from proxmox_api.config import configuration as config
from proxmox_api.db.db_functions import *

logging.basicConfig(filename=config.LOG_FILE_NAME, filemode="a", level=logging.DEBUG
                    , format='%(asctime)s ==> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

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
    except Exception as e:
        logging.error("Problem in get_user_dns: " + str(e))
        return {"dns": "error occured"}, 500


def del_user_dns(dnsid):
    entry = get_entry_host(dnsid)[0]['host']
    if entry is None:
        return {"dns": "not found"}, 404
    ddns_rep = ddns.delete_dns_record(entry)
    if ddns_rep[1] == 201:
        del_dns_entry(dnsid)
    return ddns_rep


def load_balance_server():
    nodes_info = proxmox.nodes.get()
    server = ""
    perram_min = 100
    for i in nodes_info:
        perram = round(i["mem"] * 100 / i["maxmem"], 2)
        percpu = round(i["cpu"] * 100, 2)
        if i["status"] == "online" and perram < 90 and percpu < 70:
            if perram < perram_min:
                perram_min = perram
                server = i["node"]
    if server == "":
        return {"server": "no server available"}, 500

    return {"server": server}, 201


def delete_vm(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm['vmid'] == vmid:

            try:
                if get_vm_status(vmid)[0]['status'] == 'stopped':
                    proxmox.nodes(vm["node"]).qemu(vmid).delete()
                    del_vm_list(vmid)
                    return {"state": "vm deleted"}, 201
                else:
                    stop_vm(vmid)
                    while get_vm_status(vmid)[0]['status'] != 'stopped':
                        sleep(1)
                    proxmox.nodes(vm["node"]).qemu(vmid).delete()
                    del_vm_list(vmid)
                    return {"state": "vm deleted"}, 201
            except Exception as e:
                logging.error("Problem in delete_vm: " + str(e))
                return {"state": "error"}, 500
    return {"state": "vm not found"}, 404


def create_vm(name, vm_type, user_id, password="no", vm_user="no", main_ssh_key="no"):
    next_vmid = int(proxmox.cluster.nextid.get())
    server = load_balance_server()

    if server[1] != 201:
        return server
    else:
        server = server[0]["server"]

    template_node = ""

    try:
        if vm_type == "bare_vm":

            for vm in proxmox.cluster.resources.get(type="vm"):
                if vm["vmid"] == 10000:
                    template_node = vm["node"]

            proxmox.nodes(template_node).qemu(10000).clone.create(
                name=name,
                newid=next_vmid,
                target=server,
                full=1,
            )

        elif vm_type == "nginx_vm":

            for vm in proxmox.cluster.resources.get(type="vm"):
                if vm["vmid"] == 10001:
                    template_node = vm["node"]

            proxmox.nodes(template_node).qemu(10001).clone.create(
                name=name,
                newid=next_vmid,
                target=server,
                full=0,

            )

        else:
            return {"status": "vm type not defines"}, 500

        user = get_user_id(user_id=user_id)

        if user is None:
            add_user(user_id)
            add_vm(id=next_vmid, user_id=user_id, type=vm_type)
        else:
            add_vm(id=next_vmid, user_id=user_id, type=vm_type)

    except Exception as e:
        logging.error("Problem in create_vm(" + str(next_vmid) + ") when cloning: " + str(e))
        delete_vm(next_vmid)
        return {"status": "error"}, 500

    sync = False
    while not sync:  # Synchronisation
        try:
            if "lock" not in proxmox.nodes(server)\
                    .qemu(next_vmid).status.current.get():  # Si lockée, on attend
                sync = True
            sleep(1)
        except ResourceException:  # Exception si pas encore synchronisés
            sleep(1)

    if password != "no":
        try:
            proxmox.nodes(server).qemu(next_vmid).config.create(
                cipassword=password
            )
        except Exception as e:
            logging.error("Problem in create_vm(" + str(next_vmid) + ") when setting password: " + str(e))
            delete_vm(next_vmid)
            return {"status": "error"}, 500

    if vm_user != "no":
        try:
            proxmox.nodes(server).qemu(next_vmid).config.create(
                ciuser=vm_user
            )
        except Exception as e:
            logging.error("Problem in create_vm(" + str(next_vmid) + ") when setting user: " + str(e))
            delete_vm(next_vmid)
            return {"status": "error"}, 500

    if main_ssh_key != "no":
        try:
            proxmox.nodes(server).qemu(next_vmid).config.create(
                sshkeys=urllib.parse.quote(main_ssh_key, safe='')
            )
        except Exception as e:
            logging.error("Problem in create_vm(" + str(next_vmid) + ") when setting ssh key: " + str(e))
            delete_vm(next_vmid)
            return {"status": "error"}, 500

    try:
        proxmox.nodes(server).qemu(next_vmid).status.start.create()

    except Exception as e:
        logging.error("Problem in create_vm(" + str(next_vmid) + ") when sarting VM: " + str(e))
        delete_vm(next_vmid)
        return {"status": "error"}, 500
    return {"status": "Vm created"}, 201


def start_vm(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                proxmox.nodes(vm["node"]).qemu(vmid).status.start.create()
                return {"state": "vm started"}, 201
            except Exception as e:
                logging.error("Problem in start_vm(" + str(vmid) + ") when starting VM: " + str(e))
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
            except Exception as e:
                logging.error("Problem in stop_vm(" + str(vmid) + ") when stopping VM: " + str(e))
                return {"state": "error"}, 500
    return {"state": "vm not found"}, 404


def get_vm_ip(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                ips = []
                for int in proxmox.nodes(vm["node"]).qemu(vmid).agent.get("network-get-interfaces")['result']:
                    if int['name'] != 'lo':
                        for ip in int['ip-addresses']:
                            if ip['ip-address-type'] == "ipv4":
                                ips.append(ip["ip-address"])

                return {"vm_ip": ips}, 201
            except Exception as e:
                logging.error("Problem in get_vm_ip(" + str(vmid) + ") when getting VM infos: " + str(e))
                return {"vm_ip": "error"}, 500
    return {"vm_ip": "Vm not found"}, 404


def get_vm_name(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                name = proxmox.nodes(vm["node"]).qemu(vmid).config.get()['name']
                return {"name": name}, 201
            except Exception as e:
                logging.error("Problem in get_vm_name(" + str(vmid) + ") when getting VM name: " + str(e))
                return {"name": "error"}, 500
    return {"name": "Vm not found"}, 404


def get_vm(user_id = 0):
    if user_id != 0:
        return get_vm_list(user_id), 201
    else:
        return get_vm_list(), 201


def get_vm_cpu(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                cpu = proxmox.nodes(vm["node"]).qemu(vmid).config.get()['sockets'] * \
                      proxmox.nodes(vm["node"]).qemu(vmid).config.get()['cores']
                return {"cpu": cpu}, 201
            except Exception as e:
                logging.error("Problem in get_vm_cpu(" + str(vmid) + ") when getting VM cpu: " + str(e))
                return {"cpu": "error"}, 500
    return {"cpu": "Vm not found"}, 404


def get_vm_disk(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                disk = int(proxmox.nodes(vm["node"]).qemu(vmid).config.get()['scsi0'].split('=')[-1].replace('G', ''))
                return {"disk": disk}, 201
            except Exception as e:
                logging.error("Problem in get_vm_disk(" + str(vmid) + ") when getting VM disk size: " + str(e))
                return {"disk": "error"}, 500
    return {"disk": "Vm not found"}, 404


def get_vm_ram(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            try:
                ram = proxmox.nodes(vm["node"]).qemu(vmid).config.get()['memory']
                return {"ram": ram}, 201
            except:
                return {"ram": "error"}, 500
    return {"ram": "Vm not found"}, 404


def get_vm_status(vmid):
    for vm in proxmox.cluster.resources.get(type="vm"):
        if vm["vmid"] == vmid:
            qemu_status = proxmox.nodes(vm["node"]).qemu(vmid).status.current.get()
            if "lock" in qemu_status:
                return {"status": "creating"}, 201
            try:
                qemu_agent_status = proxmox.nodes(vm["node"]).qemu(vmid).agent.ping.create()

                if qemu_agent_status:
                    qemu_agent_status = True
                else:
                    qemu_agent_status = False

                if (qemu_status['status'] == 'running') & qemu_agent_status:
                    return {"status": "running"}, 201
                if (qemu_status['status'] == 'running') & (not qemu_agent_status):
                    return {"status": "booting"}, 201
                return {"status": "stopped"}, 201

            except ResourceException:  # qemu_agent error
                if qemu_status['status'] == 'running':
                    return {"status": "booting"}, 201

                else:
                    return {"status": "stopped"}, 201

            except Exception as e:
                logging.error("Problem in get_vm_status(" + str(vmid) + ") when getting VM status: " + str(e))
                return {"status": "error"}, 500

    return {"status": "vm not found"}, 404
