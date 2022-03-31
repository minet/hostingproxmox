import urllib.parse
from time import sleep
import logging
from proxmoxer import ProxmoxAPI
from proxmoxer import ResourceException
import proxmox_api.ddns as ddns
from proxmox_api.config import configuration as config
from proxmox_api.db.db_functions import *
from ipaddress import IPv4Network
import time
logging.basicConfig(filename="log", filemode="a", level=logging.INFO
                    , format='%(asctime)s ==> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

proxmox = ProxmoxAPI(host=config.PROXMOX_HOST, user=config.PROXMOX_USER
                     , token_name=config.PROXMOX_API_KEY_NAME
                     , token_value=config.PROXMOX_API_KEY, verify_ssl=False)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')
def add_user_dns(user_id, entry, ip):
    rep_msg, rep_code = ddns.create_entry(entry, ip)
    if rep_code == 201:
        add_dns_entry(user_id, entry, ip)
        logging.info("DNS entry added: " + str(user_id) + " " + str(entry) + "=> " + str(ip))
    return rep_msg, rep_code


def get_user_dns(user_id = ""):
    try:
        if user_id != "" :
            dnsList = get_dns_entries(user_id)
            return dnsList, 201
        else :
            return get_dns_entries(), 201
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
        logging.info("DNS entry deleted: " + str(dnsid))
    return ddns_rep


def load_balance_server():
    nodes_info = proxmox.nodes.get()
    server = ""
    perram_min = 100
    for i in nodes_info:
        if i['node'] != "aomine": # on veut rien sur aomine
            perram = round(i["mem"] * 100 / i["maxmem"], 2)
            percpu = round(i["cpu"] * 100, 2)
            if i["status"] == "online" and perram < 90 and percpu < 70:
                if perram < perram_min:
                    perram_min = perram
                    server = i["node"]
    if server == "":
        return {"server": "no server available"}, 500

    return {"server": server}, 201

def is_admin(memberOf):
    if config.ADMIN_DN in memberOf:
        return True
    else:
        return False

def delete_vm(vmid, node):
    try:
        if get_vm_status(vmid, node)[0]['status'] == 'stopped':
            proxmox.nodes(node).qemu(vmid).delete()
            del_vm_list(vmid)
            return {"state": "vm deleted"}, 201
        else:
            stop_vm(vmid, node)
            while get_vm_status(vmid, node)[0]['status'] != 'stopped':
                sleep(1)
            proxmox.nodes(node).qemu(vmid).delete()
            del_vm_list(vmid)
            return {"state": "vm deleted"}, 201
    except Exception as e:
        logging.error("Problem in delete_vm: " + str(e))
        return {"state": "error"}, 500


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
            user = get_user_id(user_id=user_id)

            if user is None:
                add_user(user_id)
                add_vm(id=next_vmid, user_id=user_id, type=vm_type)
            else:
                if len(get_vm_list(user_id)) < config.LIMIT_BY_USER and len(get_vm_list()) < config.TOTAL_VM_LIMIT:
                    add_vm(id=next_vmid, user_id=user_id, type=vm_type, mac="En attente", ip="En attente")
                else:
                    return {"status": "error, can not create more VMs"}, 500
                
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
            user = get_user_id(user_id=user_id)

            if user is None:
                add_user(user_id)
                add_vm(id=next_vmid, user_id=user_id, type=vm_type)
            else:
                if len(get_vm_list(user_id)) < config.LIMIT_BY_USER and len(get_vm_list()) < config.TOTAL_VM_LIMIT:
                    add_vm(id=next_vmid, user_id=user_id, type=vm_type, mac="En attente", ip="En attente")
                else:
                    return {"status": "error, can not create more VMs"}, 500

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


def start_vm(vmid, node):
    try:
        if get_vm_status(vmid, node)[0]['status'] == 'stopped':
            proxmox.nodes(node).qemu(vmid).status.start.create()
            logging.info("VM " + str(vmid) + " started")
            return {"state": "vm started"}, 201
        else:
            return {"state": "vm already started"}, 201
    except Exception as e:
        logging.error("Problem in start_vm(" + str(vmid) + ") when starting VM: " + str(e))
        return {"status": "error"}, 500


def stop_vm(vmid, node):
    try:
        if get_vm_status(vmid, node)[0]['status'] != 'stopped':
            proxmox.nodes(node).qemu(vmid).status.stop.create()
            logging.info("VM " + str(vmid) + " stoped")
            return {"state": "vm stopped"}, 201
        else:
            return {"state": "vm already stopped"}, 201
    except Exception as e:
        logging.error("Problem in stop_vm(" + str(vmid) + ") when stopping VM: " + str(e))
        return {"state": "error"}, 500


def get_vm_ip(vmid, node):
    try:
        ips = []
        for int in proxmox.nodes(node).qemu(vmid).agent.get("network-get-interfaces")['result']:
            if int['name'] == 'eth0':
                for ip in int['ip-addresses']:
                    if ip['ip-address-type'] == "ipv4":
                        ips.append(ip["ip-address"])
                        break

        return {"vm_ip": ips}, 201
    except Exception as e:
        logging.error("Problem in get_vm_ip(" + str(vmid) + ") when getting VM infos: " + str(e))
        return {"vm_ip": "error"}, 500

def get_vm_hardware_address(vmid, node):
    return proxmox.nodes(node).qemu(vmid).agent.get("network-get-interfaces")['result'][1]['hardware-address']  # récupération de l'adresse mac de la nouvelle vm



##########################
####### DEPRECATED #######
##########################
def get_vm_autoreboot(vmid, node): # renvoie si la VM est en mode reboot auto au démarrage du noeud
    try:
        if "onboot" in proxmox.nodes(node).qemu(vmid).config.get():
            if proxmox.nodes(node).qemu(vmid).config.get()['onboot'] == 1:
                autoreboot = 1
            else:
                autoreboot = 0
        else:
            autoreboot = 0
        return {"autoreboot": autoreboot}, 201
    except Exception as e:
        logging.error("Problem in get_vm_name(" + str(vmid) + ") when getting VM autoreboot: " + str(e))
        return {"name": "error"}, 500



def get_vm_name(vmid, node):
    try:
        name = proxmox.nodes(node).qemu(vmid).config.get()['name']
        return {"name": name}, 201
    except Exception as e:
        logging.error("Problem in get_vm_name(" + str(vmid) + ") when getting VM name: " + str(e))
        return {"name": "error"}, 500


def get_vm(user_id = 0):
    if user_id != 0:
        return get_vm_list(user_id), 201
    else:
        return get_vm_list(), 201

def get_node_from_vm(vmid):
    if vmid:
        for vm in proxmox.cluster.resources.get(type="vm"):
            if vm["vmid"] == vmid:
                try:
                    return vm['node']
                except Exception as e:
                    logging.error("Problem in get_node_from_vm(" + str(vmid) + ") when getting VM node: " + str(e))
                    return {"cpu": "error"}, 500
    else:
        return {"get_node": "Vm not found"}, 404

"""Return all the configuration info related to a VM, it combines name,  cpu, disk, ram and autoreboot
"""

def get_vm_config(vmid, node):
    try:
        config = proxmox.nodes(node).qemu(vmid).config.get()
    except Exception as e :
        logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM config: " + str(e))
        return {"config": "error"}, 500
    
    # CPU : 
    try:
        cpu = config['sockets']* config['cores']
    except Exception as e :
        logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM cpu: " + str(e))
        return {"cpu": "error"}, 500


    
    # DISK 
    try :
        disk = int(config['scsi0'].split('=')[-1].replace('G', '')) 
    except Exception as e:
        logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM disk size: " + str(e))
        return {"disk": "error"}, 500
    

    # RAM : 
    try:
        ram =config['memory']
    except:
        logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM ram " + str(e))
        return {"memory": "error"}, 500


    # NAME : 
    try : 
        name = config['name']
    except Exception as e:
        logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM name: " + str(e))
        return {"name": "error"}, 500


    try:
        if "onboot" in config:
            if config['onboot'] == 1:
                autoreboot = 1
            else:
                autoreboot = 0
        else:
            autoreboot = 0
    except Exception as e:
        logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM autoreboot: " + str(e))
        return {"autoreboot": "error"}, 500

    return {"name": name, "cpu":cpu, "ram":ram, "disk":disk, "autoreboot":autoreboot}, 201



"""Return all the CURRENT status info related to a VM, it combines cpu usage, ram usage and uptime
"""

def get_vm_current_status(vmid, node):
    try:
        current_status = proxmox.nodes(node).qemu(vmid).status.current.get()
    except Exception as e:
        logging.error("Problem in get_vm_current_status(" + str(vmid) + ") when getting VM global status: " + str(e))
        return {"get_vm_current_status": "error"}, 500


    # CPU usage

    try : 
        cpu_usage = round(float(current_status['cpu'] * 100), 1)
    except Exception as e:
        logging.error("Problem in get_vm_current_status(" + str(vmid) + ") when getting VM cpu usage: " + str(e))
        return {"cpu_usage": "error"}, 500

    # RAM usage 
    try:
        ram_usage = round(float(current_status['mem'] * 100/current_status['maxmem']), 1)
    except:
        logging.error("Problem in get_vm_current_status(" + str(vmid) + ") when getting VM ram usage: " + str(e))
        return {"ram_usage": "error"}, 500
    

    # uptime 
    try:
        uptime = current_status["uptime"]
    except Exception as e:
        logging.error("Problem in get_vm_current_status(" + str(vmid) + ") when getting VM uptime: " + str(e))
        return {"uptime": "error"}, 500

    return {"cpu_usage": cpu_usage, "ram_usage":ram_usage, "uptime":uptime},201
    


##########################
####### DEPRECATED #######
##########################
def get_vm_cpu(vmid, node):
    try:
        cpu = proxmox.nodes(node).qemu(vmid).config.get()['sockets'] * \
              proxmox.nodes(node).qemu(vmid).config.get()['cores']
        return {"cpu": cpu}, 201
    except Exception as e:
        logging.error("Problem in get_vm_cpu(" + str(vmid) + ") when getting VM cpu: " + str(e))
        return {"cpu": "error"}, 500


##########################
####### DEPRECATED #######
##########################
def get_vm_cpu_usage(vmid, node):
    try:
        cpu_usage = round(float(proxmox.nodes(node).qemu(vmid).status.current.get()['cpu'] * 100), 1)
        return {"cpu_usage": cpu_usage}, 201
    except Exception as e:
        logging.error("Problem in get_vm_cpu_usage(" + str(vmid) + ") when getting VM cpu usage: " + str(e))
        return {"cpu_usage": "error"}, 500


##########################
####### DEPRECATED #######
##########################
def get_vm_disk(vmid, node):
    try:
        disk = int(proxmox.nodes(node).qemu(vmid).config.get()['scsi0'].split('=')[-1].replace('G', ''))
        return {"disk": disk}, 201
    except Exception as e:
        logging.error("Problem in get_vm_disk(" + str(vmid) + ") when getting VM disk size: " + str(e))
        return {"disk": "error"}, 500

##########################
####### DEPRECATED #######
##########################
def get_vm_ram(vmid, node):
    try:
        ram = proxmox.nodes(node).qemu(vmid).config.get()['memory']
        return {"ram": ram}, 201
    except:
        return {"ram": "error"}, 500


##########################
####### DEPRECATED #######
##########################
def get_vm_ram_usage(vmid, node):
    try:
        ram_usage = round(float(proxmox.nodes(node).qemu(vmid).status.current.get()['mem'] * 100/proxmox.nodes(node).qemu(vmid).status.current.get()['maxmem']), 1)
        return {"ram_usage": ram_usage}, 201
    except:
        return {"ram_usage": "error"}, 500




def get_vm_status(vmid, node):
    qemu_status = proxmox.nodes(node).qemu(vmid).status.current.get()
    if "lock" in qemu_status:
        return {"status": "creating"}, 201
    try:
        qemu_agent_status = proxmox.nodes(node).qemu(vmid).agent.ping.create()

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


##########################
####### DEPRECATED #######
##########################
def get_vm_uptime(vmid, node):
    try:
        uptime = proxmox.nodes(node).qemu(vmid).status.current.get()["uptime"]
        return {"uptime": uptime}, 201
    except Exception as e:
        logging.error("Problem in get_vm_uptime(" + str(vmid) + ") when getting VM uptime: " + str(e))
        return {"uptime": "error"}, 500



##########################
####### DEPRECATED #######
##########################
def update_vm_ips_job(app):    # Job to update VM ip
    with app.app_context():    # Needs application context
        for j in proxmox.cluster.resources.get(type="vm"):
            vm = Vm.query.filter_by(id=j['vmid']).first()
            if vm is not None and (vm.ip == "En attente" or vm.mac == "En attente"):
                vm.mac = get_vm_hardware_address(vm.id, j['node'])
                network = IPv4Network('157.159.195.0/24')
                reserved = {'157.159.195.1', '157.159.195.2', '157.159.195.3', '157.159.195.4', '157.159.195.5',
                            '157.159.195.6', '157.159.195.7', '157.159.195.8', '157.159.195.9',
                            '157.159.195.10'}
                hosts_iterator = (host for host in network.hosts() if str(host) not in reserved)
                for host in hosts_iterator:
                    if is_ip_available(host) == True:
                        vm.ip = host
                        break
                if vm.ip == "En attente":
                    return {"status": "No ip available"}, 500

                for k in proxmox.nodes(j['node']).qemu(j['vmid']).firewall.ipset("hosting").get():  # on vire d'abord toutes les ip set
                    cidr = k['cidr']
                    proxmox.nodes(j['node']).qemu(j['vmid']).firewall.ipset("hosting").delete(cidr)
                proxmox.nodes(j['node']).qemu(j['vmid']).firewall.ipset("hosting").create(cidr=vm.ip)  # on met l'ipset à jour
                db.session.commit()



def switch_autoreboot(vmid):
    try:
       if get_vm_autoreboot(vmid) == 1:
           proxmox.nodes(vm["node"]).qemu(vmid).config.post(onboot=0)
           return {"status": "changed"}, 201
       else:
           proxmox.nodes(vm["node"]).qemu(vmid).config.post(onboot=1)
           return {"status": "changed"}, 201
    except Exception as e:
        logging.error("Problem in get_vm_uptime(" + str(vmid) + ") when getting VM uptime: " + str(e))
        return {"uptime": "error"}, 500