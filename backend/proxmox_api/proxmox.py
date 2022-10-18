from email import header
from operator import truediv
import urllib.parse
from time import sleep
import logging
from proxmoxer import ProxmoxAPI
from proxmoxer import ResourceException
from proxmox_api.util import *
import proxmox_api.ddns as ddns
from proxmox_api.config import configuration  
from proxmox_api.db.db_functions import *
from proxmox_api.mail import sendMail, mailHTMLGenerator
from ipaddress import IPv4Network
from threading import Thread
import time
from datetime import datetime, date
import connexion
import requests
import proxmox_api.mail as mail
logging.basicConfig(filename="log", filemode="a", level=logging.INFO
                    , format='%(asctime)s ==> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


if bool(configuration.PROXMOX_HOST) and bool(configuration.PROXMOX_USER) and bool(configuration.PROXMOX_API_KEY_NAME) and bool(configuration.PROXMOX_API_KEY) :
    proxmox = ProxmoxAPI(host=configuration.PROXMOX_HOST, user=configuration.PROXMOX_USER
                     , token_name=configuration.PROXMOX_API_KEY_NAME
                     , token_value=configuration.PROXMOX_API_KEY, verify_ssl=False)
else:
    raise Exception("Environnement variables are not exported")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')






def add_user_dns(user_id, entry, ip):
    # First we check if the user own the ip
    isOk = check_dns_ip_entry(user_id, ip)
    if isOk == None :
        return {"error": "An error occured while checking your ip addresses. Please try again."}, 500
    elif not isOk : 
         return {"error": "This ip address isn't associated to one of your vms. This is illegal. This incident will be reported."}, 403

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
    if configuration.ADMIN_DN in memberOf:
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
        print("Problem in delete_vm: " + str(e))
        logging.error("Problem in delete_vm: " + str(e))
        return {"state": "error"}, 500

    """_summary_
    Create a VM with the infos given by the user
    Each info is check before the vm creation

    The first step is to clone the right VM.

    When it's done (and it can be long), the password, username, and ssh key are set up.

    The policy is to :
        initiate the VM creation.
        Return 201 status code and continue to wait for the vm to be up.
        When it's up the VM is configurate. if there is an error while configurating, the
    """
def create_vm(name, vm_type, user_id, password="no", vm_user="", main_ssh_key="no"):
    print("create vm" , name, vm,vm_type, user_id, vm_user)
    if not check_password_strength(password):
        return {"error" : "Incorrect password format"}, 400
    if not check_ssh_key(main_ssh_key):
        return {"error" : "Incorrect ssh key format"}, 400
    if not check_username(vm_user):
        return {"error" : "Incorrect vm user format"}, 400

    next_vmid = int(proxmox.cluster.nextid.get())
    node = load_balance_server()


    if node[1] != 201:
        return node
    else:
        node = node[0]["server"]

    template_node = ""
    try:
        if vm_type == "bare_vm":
            user = get_user_id(user_id=user_id)

            if user is None:
                add_user(user_id)
                add_vm(id=next_vmid, user_id=user_id, type=vm_type)
            else:
                if len(get_vm_list(user_id)) < configuration.LIMIT_BY_USER and len(get_vm_list()) < configuration.TOTAL_VM_LIMIT:
                    add_vm(id=next_vmid, user_id=user_id, type=vm_type, mac="En attente", ip="En attente")
                else:
                    return {"error": "error, can not create more VMs"}, 500

            for vm in proxmox.cluster.resources.get(type="vm"):
                if vm["vmid"] == 10000:
                    template_node = vm["node"]
            proxmox.nodes(template_node).qemu(10000).clone.create(
                name=name,
                newid=next_vmid,
                target=node,
                full=1,
            )

        elif vm_type == "nginx_vm":
            user = get_user_id(user_id=user_id)

            if user is None:
                add_user(user_id)
                add_vm(id=next_vmid, user_id=user_id, type=vm_type)
            else:
                if len(get_vm_list(user_id)) < configuration.LIMIT_BY_USER and len(get_vm_list()) < configuration.TOTAL_VM_LIMIT:
                    add_vm(id=next_vmid, user_id=user_id, type=vm_type, mac="En attente", ip="En attente")
                else:
                    return {"error": "Impossible to create more VMs"}, 403

            for vm in proxmox.cluster.resources.get(type="vm"):
                if vm["vmid"] == 10001:
                    template_node = vm["node"]

            proxmox.nodes(template_node).qemu(10001).clone.create(
                name=name,
                newid=next_vmid,
                target=node,
                full=0,

            )

        else:
            return {"error": "vm type not defines"}, 400



    except Exception as e:
        logging.error("Problem in create_vm(" + str(next_vmid) + ") when cloning: " + str(e))
        print("Problem in create_vm(" + str(next_vmid) + ") when cloning: " + str(e))
        delete_vm(next_vmid, node)
        return {"error": "Impossible to create the VM (cloning)"}, 500
    

    if not update_vm_status(next_vmid, "creating"):
        print("Problem while updating the vm status")
        delete_vm(next_vmid, node)
        return {"error": "Impossible to update the VM status"}, 500
    Thread(target=config_vm, args=(next_vmid, node, password, vm_user, main_ssh_key, )).start()
    return {"vmId": next_vmid}, 201



    """After the vm creation (ie the vm clone) we wait for it to be up to config it
    When the VM is up, the password, vm user name and ssh key are set up
    """
def config_vm(vmid, node, password, vm_user,main_ssh_key):
    sync = False
    vm = proxmox.nodes(node).qemu(vmid)
    while not sync:  # Synchronisation
        try:
            if "lock" not in vm.status.current.get():  # Si lockée, on attend

                sync = True
            sleep(1)
        except ResourceException:  # Exception si pas encore synchronisés
            sleep(1)

   

    try:
        vm.config.create(
            cipassword=password
        )
    except Exception as e:
        update_vm_status(vmid,"An error occured while setting your password (vmid ="+str(vmid) +")", errorCode=500)
        logging.error("Problem in create_vm(" + str(vmid) + ") when setting password: " + str(e))
        return delete_vm(vmid, node)


    try:
        vm.config.create(
            ciuser=vm_user
        )
    except Exception as e:
        update_vm_status(vmid,"An error occured while creating the user  (vmid ="+str(vmid) +")", errorCode=500)
        logging.error("Problem in create_vm(" + str(vmid) + ") when setting user: " + str(e))
        return delete_vm(vmid, node)
        

    try:
        vm.config.create(
            sshkeys=urllib.parse.quote(main_ssh_key, safe='')
        )
    except Exception as e:
        update_vm_status(vmid,"An error occured while setting your ssh key (vmid ="+str(vmid) +")", errorCode=500)
        logging.error("Problem in create_vm(" + str(vmid) + ") when setting ssh key: " + str(e))
        return delete_vm(vmid, node)

    # We give an ip to the VM before it starts 
    #try : 
    #        dbVM = get_vm_db_info()
    #        print("dbVM = " , dbVM)
    #        (body, status) = update_vm_ip_address(dbVM, node, debug=True)
    #        if status != 201:
    #            update_vm_status(vmid,"An error" + str(status) + " occured while setting your ip #address (vmid ="+str(vmid) +")", errorCode=500)
    #            logging.error("Problem in create_vm(" + str(vmid) + ") when updating ips")
    #            print("Problem in create_vm(" + str(vmid) + ") when updating ips: " ,body, status )
    #            return delete_vm(vmid, node)
    #       
    #except Exception as e: 
    #    update_vm_status(vmid,"An unkonwn error occured while setting your ip address (vmid ="+str#(vmid) +")", errorCode=500)
    #    logging.error("Problem in create_vm(" + str(vmid) + ") when updating ips." )
    #    print("Problem in create_vm(" + str(vmid) + ") when updating ips: ", e )
    #    #return delete_vm(vmid, node)
    #    return 1

    try:
        vm.status.start.create()

    except Exception as e:
        update_vm_status(vmid,"An unkonwn error occured while starting your vm(vmid ="+str(vmid) +")", errorCode=500)
        logging.error("Problem in create_vm(" + str(vmid) + ") when sarting VM: " + str(e))
        return delete_vm(vmid, node)


    # if we are here then the VM is well created
    update_vm_status(vmid, "created")
    


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

        return {"vm_ip": ips}, 200
    except Exception as e:
        logging.error("Problem in get_vm_ip(" + str(vmid) + ") when getting VM infos: " + str(e))
        return {"error ": "Impossible to get info about your vm"}, 500

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
    print("get node for ", vmid)
    if vmid:
        for vm in proxmox.cluster.resources.get(type="vm"):
            if vm["vmid"] == vmid:
                try:
                    return vm['node']
                except Exception as e:
                    logging.error("Problem in get_node_from_vm(" + str(vmid) + ") when getting VM node: " + str(e))
                    print("Problem in get_node_from_vm(" + str(vmid) + ") when getting VM node: " + str(e))
                    return {"error": "Impossible to retrieve the vm node"}, 500
    else:
        print("Error : vmid is null")
        return {"get_node": "Vm not found"}, 404

"""
If the vm is creating then we return its state if not : 

Return all the configuration info related to a VM, it combines name,  cpu, disk, ram and autoreboot if created 
"""

def get_vm_config(vmid, node):
    # first we check the vm creation status : 
    vm_creation = vm_creation_status(vmid)
    if vm_creation != None : # if not then the vm is created of not found
        (status, httpErrorCode, errorMessage) = vm_creation 
        if status == "error":
            update_vm_status(vmid, "delete", deleteEntry= True) # We send to the user and delete here
            try : 
                return {"error", errorMessage}, httpErrorCode
            except: 
                return {"error", "An unknown error occured"}, 500
        elif status == "creating" : 
            return {"status" : "creating"}, 200
        elif  status == "created" : 
            update_vm_status(vmid, "delete", deleteEntry= True) # We send to the user and delete here
            return {"status": "created"}, 201
        else :
            return {"error": "Unknown vm status"}, 400
            
    else : 
        start = time.time()
        try:
            config = proxmox.nodes(node).qemu(vmid).config.get()
        except Exception as e :
            logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM config: " + str(e))
            print("Problem in get_vm_config(" + str(vmid) + ") when getting VM config: " + str(e))
            return {"error": "An error occured while configuring your vm" + str(e)}, 500

        # CPU :
        try:
            cpu = config['sockets']* config['cores']
        except Exception as e :
            logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM cpu: " + str(e))
            print("Problem in get_vm_config(" + str(vmid) + ") when getting VM cpu: " + str(e))
            return {"error": "An error occured while setting the VM CPU"}, 500



        # DISK
        try :
            disk = int(config['scsi0'].split('=')[-1].replace('G', ''))
        except Exception as e:
            logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM disk size: " + str(e))
            print("Problem in get_vm_config(" + str(vmid) + ") when getting VM disk size: " + str(e))
            return {"error": "An error occured while setting the VM disk"}, 500


        # RAM :
        try:
            ram =config['memory']
        except:
            print("Problem in get_vm_config(" + str(vmid) + ") when getting VM ram " + str(e))
            logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM ram " + str(e))
            return {"error": "An error occured while setting the VM RAM"}, 500

        # NAME :
        try :
            name = config['name']
        except Exception as e:
            logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM name: " + str(e))
            print("Problem in get_vm_config(" + str(vmid) + ") when getting VM name: " + str(e))
            return {"error": "An error occured while setting the VM name"}, 500


        try:
            if "onboot" in config:
                if config['onboot'] == 1:
                    autoreboot = 1
                else:
                    autoreboot = 0
            else:
                autoreboot = 0
        except Exception as e:
            print("Problem in get_vm_config(" + str(vmid) + ") when getting VM autoreboot: " + str(e))
            logging.error("Problem in get_vm_config(" + str(vmid) + ") when getting VM autoreboot: " + str(e))
            return {"error": "An error occured while setting setting the autoreboot option"}, 500
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
        return {"error": "Impossible to retrieve the parameter : uptime"}, 500

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
        return {"error": "Impossible to retrieve uptime "}, 500



def update_vm_ips_job(app):    # Job (schedules each 10s) to update all VMs' ip
    #start = time.time()
    #
    # print("test")
    with app.app_context():    # Needs application context
        for j in proxmox.cluster.resources.get(type="vm"):
            #print("j=", j)
            vm = Vm.query.filter_by(id=j['vmid']).first()
            if vm != None:
                #print("vm =", vm)
                node = j["node"]
                #print("ip updating ...")
                try:
                    update_vm_ip_address(vm, node)
                except Exception as e:
                    print("Impossible to update the ip of  vm " , j['vmid'] , e)
                #print("ip updated")
            
   #print("update vm finish, took", time.time() - start , "s")
   

# Update the VM ip address
# The debug mode is optionnal and test if a ip was well updated
def update_vm_ip_address(vm, node, debug=False):
    #print("update vm ip", vm, node, debug)
    if vm is not None and (vm.ip == "En attente" or vm.mac == "En attente"):
        vm.mac = get_vm_hardware_address(vm.id, node)
        network = IPv4Network('157.159.195.0/24')
        reserved = {'157.159.195.1', '157.159.195.2', '157.159.195.3', '157.159.195.4', '157.159.195.5',
                    '157.159.195.6', '157.159.195.7', '157.159.195.8', '157.159.195.9',
                    '157.159.195.10'}
        hosts_iterator = (host for host in network.hosts() if str(host) not in reserved)
        for host in hosts_iterator:
            if is_ip_available(host) == True:
                vm.ip = host
                if debug:
                    print("DEBUG : attribution of " + host + "for vm" + vm.id )
                break
        if vm.ip == "En attente":
            print("WARNING : THERE IS NO IP AVAILABLE")
            return {"error": "No ip available"}, 500
        for k in proxmox.nodes(node).qemu(vm.id).firewall.ipset("hosting").get():  # on vire d'abord toutes leip set
            cidr = k['cidr']
            proxmox.nodes(node).qemu(vm.id).firewall.ipset("hosting").delete(cidr)
        proxmox.nodes(node).qemu(vm.id).firewall.ipset("hosting").create(cidr=vm.ip)  # on met l'ipset à jour
        db.session.commit()
        return {"status": "Success"}, 201
    else : 
        if vm is None :
            if debug:
                print("DEBUG : Error while updating a VM. vm = None. This error must be investigate and lead to unable a VM to get an ip address.")
            return {"error": "Impossible to set the vm ip address"}, 500
    return {"error": "Impossible to set the vm ip address (no info)"}, 500
           


def switch_autoreboot(vmid,node):
    print(get_vm_autoreboot(vmid, node))
    (config, status) = get_vm_autoreboot(vmid, node)
    if status != 201 :
        return {"error" : "Impossible to retrieve onboot status"}, 500
    try:
       if config["autoreboot"] == 1:
           request = proxmox.nodes(node).qemu(vmid).config.post(onboot=0)
           status = get_vm_autoreboot(vmid, node)
           return {"status": "changed to 0"}, 201
       else:
           request = proxmox.nodes(node).qemu(vmid).config.post(onboot=1)
           status = get_vm_autoreboot(vmid, node)
           return {"status": "changed to 1"}, 201
    except Exception as e:
        logging.error("Problem in get_vm_uptime(" + str(vmid) + ") when getting VM uptime: " + str(e))
        print("Problem in get_vm_uptime(" + str(vmid) + ") when getting VM uptime: " + str(e))
        return {"error": "Impossible to update the uptime"}, 500



"""Check if the dns ip entry is acceptable, ie if the user own the ip. The availability of its ip address if check by ddns.py

    :param entry: the ip to check

    :return: True if the ip is acceptable 
    :rtype: bool
"""
def check_dns_ip_entry(user_id, ip:str) -> bool:
    try : 
        ip_list = get_user_ip_list(user_id)
        if ip_list == None: 
            print("ERROR : the vm list of user " , user_id, " failed to be retrieved : " , e)
            return None 
        isOk = ip in ip_list
        if not isOk :
            print("INCIDENT REPORT : the user", user_id, " tried to set up a DNS entry for ip", ip, "he doesn't own.")
        return isOk
    except Exception as e: 
        print("ERROR : the vm list of user " , user_id, " failed to be retrieved : " , e)
        return None 



def get_user_ip_list(user_id) :
    try : 
        vm_id_list = get_vm_list(user_id)
        ip_list = [] # ip of the user
        for vmid in vm_id_list:
            node = get_node_from_vm(vmid)
            vm_ip, status = get_vm_ip(vmid, node)
            if status == 200:
                ip_list += vm_ip["vm_ip"]
        return ip_list
    except Exception as e: 
        print("ERROR : the vm list of user " , user_id, " failed to be retrieved : " , e)
        return None 



""" API endpoint to return the freeze status of a user (only the status, not the nb of notification recieved)

    :param entry: username of the user asking for the freeze status

    :return: httpcode, {"freezeState" : Freeze state}
    :rtype: int, dict
"""
def get_freeze_state(username):
    #msg = mailHTMLGenerator(4, date.today(), 1)
    #print(msg)
    #sendMail("nathanstchepinsky@gmail.com", msg)
    try :
        freezeState = getFreezeState(username)
    except Exception as e : 
        print("ERROR : the freeze state of user " , username, " failed to be retrieved : " , e)
        return {"error": "Impossible to retrieve the freeze state"}, 500
    if freezeState == None: # We have to create the freeze state
        return check_update_cotisation(username)
    elif freezeState == "0.0":
        status = freezeState.split(".")[0]
        return {"freezeState" : status}, 200
    else:
        freezeState = getFreezeState(username) # if expired with update in case of re-cotisation
        status = freezeState.split(".")[0]
        return {"freezeState" : status}, 200
        
        




"""func called by jobs. For all user, it calls a function to check if the user has a cotisation. 

    :param entry: None

    :return: None
    :rtype: None
"""
def check_cotisation_job(app):
     print("check_update_cotisation_job")
     with app.app_context():    # Needs application context
        users = get_active_users()
        
        
        for user in users:
            try :
                status = check_update_cotisation(user)
                print("check_update_cotisation for user", user, " : ", status)
            except Exception as e:
                print("exception : ",e)
                pass
        db.session.commit()



"""func called by when cotisation is expired in case of recosition. For a userId it checks thecotisation, update the date if needed in the database. The send of email is done by Jenkins  (according to the frozen level (see wiki.minet.net))

    :param entry: userId : string

    :return: status code, {"status": "ok"} if the cotisation is ok, {"status": "expired"} if the cotisation is expired, {"error": "error message"} if there is an error
    :rtype: int, dict
"""
def check_update_cotisation(username):
        
        print("check cotisation of", username)
        #headers = {"Authorization": req_headers}
        headers = {"X-API-KEY": config.ADH6_API_KEY}
        #print("https://adh6.minet.net/api/member/?limit=25&filter%5Busername%5D="+str(username)+"&only=id,username")
        userInfo = requests.get("https://adh6.minet.net/api/member/?limit=25&filter%5Busername%5D="+str(username)+"&only=id,username", headers=headers) # [id,username], from ADH6 
        print("userInfo : ", userInfo)
        
        
        if userInfo == None or  userInfo.json() == []: # not found
            if "-" in username:
                print("ERROR : the user " + username + " is not found in ADH6. Try with", end='')
                new_username = username.replace("-","_") # hosting replace by default _ with -. So we try if not found
                print("'"+new_username+"'")
                return check_update_cotisation(new_username)
                
            elif "_" in username: # same
                print("ERROR : the user " + username + " is not found in ADH6. Try with", end='')
                new_username = username.replace("_",".").strip() # hosting replace by default _ with -. So we try if not found
                print("'"+new_username+"'")
                return check_update_cotisation(new_username)
            else :
                print("ERROR : the user " , username , " failed to be retrieved :" , userInfo.json())
                return {"error" : "the user " + username + " failed to be retrieved"}, 404
        else : 
            username = username.replace("_", "-") # hosting replace by default _ and .  with -.
            userId = userInfo.json()[0]["id"]
            membership = requests.get("https://adh6.minet.net/api/member/"+str(userId), headers=headers) # memership info
            membership_dict = membership.json()
            today =  date.today()
            print("membership : ", membership_dict)
            if "ip" not in membership_dict: # Cotisation expired
                #print(username , "cotisation expired", membership.json())
                print(username , "cotisation expired")
                
                #return expiredCotisation(username, userEmail) #, datetime.strptime(membership_dict["departureDate"], "%Y-%m-%d").date())
                status = getFreezeState(username)
                return {"freezeState": status}, 200
    
            else :  # we check anyway if the departure date is in the future
                #print(membership.json()["ip"])
                #print(membership.json()["departureDate"], end='\n\n')
                departureDate = datetime.strptime(membership_dict["departureDate"], "%Y-%m-%d").date()
                if departureDate < today: # Cotisation expired:
                    print(username , "cotisation expired")
                    status = getFreezeState(username)
                    return {"freezeState": status}, 200
    
                else :
                    print(username, "cotisation up to date")
                    updateFreezeState(username, "0.0")
                    return  {"freezeState": "0.0"}, 200

            

            
#####
# For the jenkins script
####

        
def expiredCotisation(username, userEmail): # Call when the cotisation is expired
    lastNotification = getLastNotificationDate(username)
    if lastNotification == None : 
        #return sendNotification(username, userEmail)
        return {"freezeState": status}, 200
    else :
        lastNotification = datetime.strptime(lastNotification,  "%Y-%m-%d").date()
        delta = date.today() - lastNotification
        #if delta.days >=7 : # We update update the status : 
        #    return sendNotification(username, userEmail)
        # We don't change the status : 
        

def sendNotification(username,userEmail): # send a notification to the user when the cotisation is expired
    freezeState = getFreezeState(username)
    status, nbNotif = generateNewFreezeState(freezeState)

    print("send a notification to " + str(username) + "with status" +str(status) + "and nbNotif" + str(nbNotif))
    # when the notification is sent : 
    updateLastNotificationDate(username, date.today())
    updatedfreezeState = str(status) + "." + str(nbNotif)
    updateFreezeState(username, updatedfreezeState)
    return  {"freezeState": updatedfreezeState}, 200
    
    

        

