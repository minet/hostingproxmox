import urllib.parse
from time import sleep
import logging
from ipaddress import IPv4Network
from threading import Thread
import time
from datetime import datetime, date
from proxmoxer import ProxmoxAPI
from proxmoxer import ResourceException
from proxmox_api import util
from proxmox_api import config
from proxmox_api import ddns
from proxmox_api.config import configuration

from proxmox_api.db import db_functions as database
from  proxmox_api.db import db_models
logging.basicConfig(filename="log", filemode="a", level=logging.INFO
                    , format='%(asctime)s ==> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
HASPROXMOXHOST = bool(configuration.PROXMOX_HOST)
HASPROXMOXUSER = bool(configuration.PROXMOX_USER)
HASPROXMOXAPIKEY = bool(configuration.PROXMOX_API_KEY)
HASPROXMOXAPIKEYNAME = bool(configuration.PROXMOX_API_KEY_NAME)
if  HASPROXMOXHOST and HASPROXMOXUSER and HASPROXMOXAPIKEY and HASPROXMOXAPIKEYNAME :
    proxmox = ProxmoxAPI(host=configuration.PROXMOX_HOST, user=configuration.PROXMOX_USER
                     , token_name=configuration.PROXMOX_API_KEY_NAME
                     , token_value=configuration.PROXMOX_API_KEY, verify_ssl=False)
else:
    raise Exception("Environnement variables are not exported")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')



def add_user_dns(user_id, entry, ip):
    
    

    rep_msg, rep_code = ddns.create_entry(entry, ip)
    if rep_code == 201:
        database.add_dns_entry(user_id, entry, ip)
        logging.info("DNS entry added: " + str(user_id) + " " + str(entry) + "=> " + str(ip))
    return rep_msg, rep_code


def get_user_dns(user_id = ""):
    try:
        if user_id != "" :
            dnsList = database.get_dns_entries(user_id)
            return dnsList, 201
        return database.get_dns_entries(), 201
    except Exception as e:
        logging.error("Problem in get_user_dns: " + str(e))
        return {"dns": "error occured"}, 500


def del_user_dns(dnsid):
    entry = database.get_entry_host(dnsid)[0]['host']
    if entry is None:
        return {"dns": "not found"}, 404
    ddns_rep = ddns.delete_dns_record(entry)
    if ddns_rep[1] == 201:
        database.del_dns_entry(dnsid)
        logging.info("DNS entry deleted: " + str(dnsid))
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

def is_admin(memberOf):
    return configuration.ADMIN_DN in memberOf


"""delete a vm by id in the database and its dns entires
:param vmid: vmid to delete
:type vmid: string
:rtype: True if success else False
"""
def delete_from_db(vmid) -> bool:
    try :
        app = util.create_app() # we need the context to delete the vm if there is an error
        db_models.db.init_app(app.app)
        with app.app.app_context():
            database.del_vm_list(vmid)
        return True
    except Exception as e :
        print("Problem in delete_vm: " + str(e))
        logging.error("Problem in delete_vm: " + str(e))
        return False


"""delete a dns record by ip in the database and DNS when a vm is deleted
:param vmid: vmid related 
:type vmid: string
:rtype:None
"""
def delete_from_dns(vmid):
    try:
        app = util.create_app() # we need the context to delete the vm if there is an error
        db_models.db.init_app(app.app)
        with app.app.app_context():
           
            ip = database.get_vm_ip(vmid)
            dns_entries = database.get_dns_entry_from_ip(ip)
            print("delete_from_dns ip = " ,ip, " dns_entries = ", dns_entries)
            for id in dns_entries:
                del_user_dns(id)
            database.delete_ip_dns_record(ip)
            return True
    except Exception as e :
        print("Problem in delete_vm: " + str(e))
        logging.error("Problem in delete_vm: " + str(e))
        return False



"""delete a vm by id and node from proxmox
:param vmid: vmid to delete
:type vmid: string
:param node: node of the vmid to delete
:type node: string
:rtype: True if success else False
"""
def delete_from_proxmox(vmid, node) -> bool :
    try:
        if get_proxmox_vm_status(vmid, node)[0]['status'] != 'stopped':
            sync = False
            while not sync:  # Synchronisation
                try:
                    # Si lockée, on attend
                    if "lock" not in get_proxmox_vm_status(vmid, node)[0]['status']:
                        sync = True
                        sleep(1)
                except ResourceException:  # Exception si pas encore synchronisés
                    sleep(1)
            stop_vm(vmid, node)
            # Si lockée, on attend:
            while get_proxmox_vm_status(vmid, node)[0]['status'] != 'stopped' :
                sleep(1)
                print("sleep")
        proxmox.nodes(node).qemu(vmid).delete() # need to wait for the deletion but work
        sync = False # we wait for the deletion to be done
        counter = 0 # after 2 min of sync, we timeout
        while not sync:
            if counter >= 120 :
                print("Deleting the vm " , vmid, " timed out")
                return {"error": "Timeout while deleting the vm"}, 500
            try:
                get_proxmox_vm_status(vmid, node)[0]['status']
                counter += 1
                sleep(1)
            except ResourceException: # The VM cannot be retrieved : it is deleted
                sync = True
        return True
    except Exception as e:
        print("Problem in delete_vm: " + str(e))
        logging.error("Problem in delete_vm: " + str(e))
        return False



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
def create_vm(name, vm_type, user_id, cpu, ram, disk, password="no", vm_user="", main_ssh_key="no"):
    if not util.check_password_strength(password):
        return {"error" : "Incorrect password format"}, 400
    if not util.check_ssh_key(main_ssh_key):
        return {"error" : "Incorrect ssh key format"}, 400
    if not util.check_username(vm_user):
        return {"error" : "Incorrect vm user format"}, 400

    next_vmid = int(next_available_vmid())
    node = load_balance_server()

    if configuration.ENVIRONMENT == "DEV":
        name = "hosting-dev-" + name

   
    if node[1] != 201:
        return {"error": "Impossible to find an available server"}, 500
    else:
        node = node[0]["server"]

    ip = set_new_vm_ip(next_vmid, node)
    if ip is None : 
        return {"error": "Impossible to attribute your IP address."}, 500

    template_node = ""
    try:
        template_id = -1
        if vm_type == "bare_vm" and disk == 10:
            template_id = 1010
        elif vm_type == "bare_vm" and disk == 20:
            template_id = 1020
        elif vm_type == "bare_vm" and disk == 30:
            template_id = 1021
        elif vm_type == "nginx_vm":
            template_id = 10001
        else :
            return {"error": "vm type not defines"}, 400

        user = database.get_user_list(user_id=user_id)
        if user is None:
            database.add_user(user_id)
            check_update_cotisation(user_id)
            database.add_vm(id=next_vmid, user_id=user_id, type=vm_type, mac="En attente", ip=ip)
            util.subscribe_to_hosting_ML(user_id)
        else:
            util.subscribe_to_hosting_ML(user_id)
            if len(database.get_vm_list(user_id)) < configuration.LIMIT_BY_USER and len(database.get_vm_list()) < configuration.TOTAL_VM_LIMIT:
                database.add_vm(id=next_vmid, user_id=user_id, type=vm_type, mac="En attente", ip=ip)
                database.add_ip_to_history(ip, next_vmid, user_id)
            else:
                return {"error": "error, can not create more VMs"}, 500
        
        template_node, status =  get_node_from_vm(template_id)
        if status != 200:
            return {"error": "Impossible to find the template"}, 500
        proxmox.nodes(template_node).qemu(template_id).clone.create(
            name=name,
            newid=next_vmid,
            target=node,
            full=1,
            storage="replicated_3_times_hosting"
        )




    except Exception as e:
        logging.error("Problem in create_vm(" + str(next_vmid) + ") when cloning: " + str(e))
        print("Problem in create_vm(" + str(next_vmid) + ") when cloning: " + str(e))
        delete_from_proxmox(next_vmid, node)
        delete_from_dns(next_vmid)
        delete_from_db(next_vmid)
        return {"error": "Impossible to create the VM (cloning)"}, 500

    app = util.create_app() # we need the context to delete the vm if there is an error
    db_models.db.init_app(app.app)
    with app.app.app_context():
        database.set_vm_status(next_vmid, "creating")
    Thread(target=config_vm, args=(next_vmid, node, password, vm_user, main_ssh_key,ip,cpu, ram, )).start()
    
    return {"vmId": next_vmid}, 201



"""After the vm creation (ie the vm clone) we wait for it to be up to config it
When the VM is up, the password, vm user name and ssh key are set up
"""
def config_vm(vmid, node, password, vm_user,main_ssh_key, ip, cpu, ram):
    
    success = True
    sync = False
    vm = proxmox.nodes(node).qemu(vmid)
    while not sync:  # Synchronisation
        try:
            if "lock" not in vm.status.current.get():  # Si lockée, on attend

                sync = True
            sleep(1)
        except ResourceException:  # Exception si pas encore synchronisés
            sleep(1)

    if cpu == 2 or cpu % 2 == 1:
        vm_socket = 1
        vm_cores = int(cpu)
    else :
        vm_socket = 2
        vm_cores = int(cpu//2)
    vm_ram = int(float(ram))*1024
    try:
        vm.config.create(
            cipassword=password,
            ciuser=vm_user,
            searchdomain="minet.net",
            nameserver="157.159.195.51",
            ipconfig0= "ip=" + str(ip)+"/24,gw=157.159.195.1",
            sshkeys=urllib.parse.quote(main_ssh_key, safe=''),
            sockets=vm_socket,
            cores=vm_cores,
            memory=vm_ram
        )
    except Exception as e:
        success = False
        logging.error("Problem in create_vm(" + str(vmid) + ") when configuring vm: " + str(e))
        print("Problem in create_vm(" + str(vmid) + ") when configuring vm: " + str(e))
        delete_from_proxmox(vmid, node)
        delete_from_dns(vmid)
        delete_from_db(vmid)
        app = util.create_app() # we need the context to delete the vm if there is an error
        db_models.db.init_app(app.app)
        with app.app.app_context():
            database.set_vm_status(vmid, "error:An error occured while configuring vm (vmid ="+str(vmid) +")")

    print("vm configured")

    try:
        vm.status.start.create()

    except Exception as e:
        success = False
        delete_from_proxmox(vmid, node)
        delete_from_dns(vmid)
        delete_from_db(vmid)
        app = util.create_app() # we need the context to delete the vm if there is an error
        db_models.db.init_app(app.app)
        with app.app.app_context():
            database.set_vm_status(vmid, "error:An error occured while configuring vm (vmid ="+str(vmid) +")")
        logging.error("Problem in create_vm(" + str(vmid) + ") when sarting VM: " + str(e))
        print("Problem in create_vm(" + str(vmid) + ") when sarting VM: " + str(e))
    print("vm started")
    try : 

        try:
            proxmox.nodes(node).qemu(vmid).firewall.ipset.hosting.get()
        except:
            proxmox.nodes(node).qemu(vmid).firewall.ipset.create(name="hosting")
        try:
            proxmox.nodes(node).qemu(vmid).firewall.ipset.hosting(ip).get()
        except:
            proxmox.nodes(node).qemu(vmid).firewall.ipset("hosting").create(cidr=ip)
        
        # order matters
        proxmox.nodes(node).qemu(vmid).firewall.options.put(enable=1)
        proxmox.nodes(node).qemu(vmid).firewall.options.put(ipfilter=0)
        proxmox.nodes(node).qemu(vmid).firewall.options.put(policy_in="ACCEPT")
        proxmox.nodes(node).qemu(vmid).firewall.rules.post(action="DROP", type="out", log="nolog", enable=1) # OUT DROP -log nolog
        proxmox.nodes(node).qemu(vmid).firewall.rules.post(action="DROP", type="in", log="nolog", enable=1) # IN DROP -log nolog
        proxmox.nodes(node).qemu(vmid).firewall.rules.post(action="ACCEPT", type="in", dest="+hosting", log="nolog", enable=1) # IN ACCEPT -dest +hosting -log nolog
        proxmox.nodes(node).qemu(vmid).firewall.rules.post(action="ACCEPT", type="out", source="+hosting", log="nolog", enable=1) # OUT ACCEPT -source +hosting -log nolog
        
        #db.session.commit()
    except Exception as e:
        success = False
        delete_from_proxmox(vmid, node)
        delete_from_dns(vmid)
        delete_from_db(vmid)
        app = util.create_app() # we need the context to delete the vm if there is an error
        db_models.db.init_app(app.app)
        with app.app.app_context():
            database.set_vm_status(vmid, "An unkonwn error occured while setting the firewall of your vm(vmid ="+str(vmid) +")")
        logging.error("Problem in create_vm(" + str(vmid) + ") when setting the firewall of VM: " + str(e))
        print("Problem in create_vm(" + str(vmid) + ") when setting the firewall of VM: " + str(e))
    print("firewall set")

    if success:
        app = util.create_app() # we need the context to delete the vm if there is an error
        db_models.db.init_app(app.app)
        with app.app.app_context():
            database.set_vm_status(vmid, "created")
    else : 
        app = util.create_app() # we need the context to delete the vm if there is an error
        db_models.db.init_app(app.app)
        with app.app.app_context():
            database.set_vm_status(vmid, "error:An error occured while creating your vm")


def start_vm(vmid, node):
    try:
        if get_proxmox_vm_status(vmid, node)[0]['status'] == 'stopped':
            proxmox.nodes(node).qemu(vmid).status.start.create()
            logging.info("VM " + str(vmid) + " started")
            return {"state": "vm started"}, 201
        else:
            return {"state": "vm already started"}, 201
    except Exception as e:
        logging.error("Problem in start_vm(" + str(vmid) + ") when starting VM: " + str(e))
        return {"status": "error"}, 500

def reboot_vm(vmid, node):
    try:
        proxmox.nodes(node).qemu(vmid).status.reboot.create()
        logging.info("VM " + str(vmid) + " rebooted")
        return {"state": "vm rebooted"}, 201
    except Exception as e:
        print("Problem in reboot_vm(" + str(vmid) + ") when starting VM: " + str(e))
        logging.error("Problem in reboot_vm(" + str(vmid) + ") when starting VM: " + str(e))
        return {"status": "An error occur while rebooting the vm"}, 500

def renew_ip(vmid):
    node, status = get_node_from_vm(vmid)
    if status != 200:
        return node, status
    try:
        ip = database.get_vm_ip(vmid)
        proxmox.nodes(node).qemu(vmid).config.post(
        searchdomain="minet.net", 
        nameserver="157.159.195.51",
        ipconfig0= "ip=" + str(ip)+"/24,gw=157.159.195.1"
        )
    except Exception as e:
        print("Problem in renew_ip(" + str(vmid) + ") when updating ip address: " + str(e))
        logging.error("Problem in renew_ip(" + str(vmid) + ") when updating ip address: " + str(e))
        return {"status": "error updating your ip address."}, 500

def update_vm_credentials(vmid,username, password, sshKey):
    node,status = get_node_from_vm(vmid)
    if status != 200:
        return node, status
    try :
        ip = database.get_vm_ip(vmid)
        proxmox.nodes(node).qemu(vmid).config.post(
        ciuser=username,
        cipassword=password,
        sshkeys=[urllib.parse.quote(sshKey, safe='')],
        searchdomain="minet.net", 
        nameserver="157.159.195.51",
        ipconfig0= "ip=" + str(ip)+"/24,gw=157.159.195.1")
        try : 
            database.setNeedToBeRestored(vmid, False)
            return {"status" :"ok"},200
        except Exception as e:
            return {"status": "Problem while updatig the VM(" + str(vmid) + ") status : " + str(e)}, 500
    except Exception as e:
        logging.error("Problem in update_vm_credentials(" + str(vmid) + ") when updating VM: " + str(e))
        return {"status": "Problem while updatig the VM(" + str(vmid) + ") : " + str(e)}, 400


def stop_vm(vmid, node):
    try:
        if get_proxmox_vm_status(vmid, node)[0]['status'] != 'stopped':
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

######
## DEPRECATED
######

def get_vm_hardware_address(vmid, node):
    # récupération de l'adresse mac de la nouvelle vm
    return proxmox.nodes(node).qemu(vmid).agent.get("network-get-interfaces")['result'][1]['hardware-address']  





def get_vm_name(vmid, node):
    try:
        name = proxmox.nodes(node).qemu(vmid).config.get()['name']
        return {"name": name}, 201
    except Exception as e:
        logging.error("Problem in get_vm_name(" + str(vmid) + ") when getting VM name: " + str(e))
        return {"name": "error"}, 500


def get_vm(user_id = 0, search=None):
    if user_id != 0: # No filter for non admin
        return database.get_vm_list(user_id), 200
    else:
        if search is None : 
            return database.get_vm_list(), 200
        else: # We get all user/name and filter them
            user_filtered = database.get_user_list(searchItem=search) # get all user filtered
            print("user_filtered = " , user_filtered)
            vm_filtered_list = []
            for user in user_filtered:
                vm_filtered_list += database.get_vm_list(user_id = user.id)
            start = time.time()
            vm_list = database.get_vm_list() # get all vm but only id
            for vmid in vm_list:
                if search in str(vmid):
                    if vmid not in vm_filtered_list:
                        vm_filtered_list.append(vmid)
                node, status = get_node_from_vm(vmid)
                if status == 200:
                    if status != 200:
                        return node, status
                if vmid not in vm_filtered_list :
                    infos,_ = get_vm_name(vmid, node)
                    name = infos["name"]
                    if search in name :
                        if vmid not in vm_filtered_list:
                            vm_filtered_list.append(vmid)
            print("time to filter proxmxo = ", time.time() - start)
            return vm_filtered_list, 200


# Checks if a vmid is available on the cluster for a new vm to be created
def is_vmid_available_cluster(vmid): 
    kars, wammu = False, False
    try :
        proxmox.nodes("kars").qemu(vmid).status.get()
        kars = True 
    except : 
        try : 
            proxmox.nodes("kars").lxc(vmid).status.get() # We have to check CT too
            kars = True
        except:
            kars = False
    try :
        proxmox.nodes("wammu").qemu(vmid).config.get()['name']
        wammu = True
    except :
        try :
            proxmox.nodes("wammu").lxc(vmid).status.get() # We have to check CT too
            wammu = True
        except:
            wammu = False
    return not kars and not wammu 



def get_node_from_vm(vmid):
    node = ""
    if vmid:
        for vm in proxmox.cluster.resources.get(type="vm"):
            if vm["vmid"] == vmid:
                try:
                    node = vm['node']
                except Exception as e:
                    logging.error("Problem in get_node_from_vm(" + str(vmid) + ") when getting VM node: " + str(e))
                    return {"cpu": "error"}, 500
        if node == "":
            return {"get_node": "Vm not found"}, 404 
        else : 
            return node, 200
    else:
        return {"get_node": "Vmid incorrect"}, 404

"""
If the vm is creating then we return its state if not : 

The vm state, ie creating or deleting must be check before. This only get the proxmox vm config

Return all the configuration info related to a VM, it combines name,  cpu, disk, ram and autoreboot if created 
"""

def get_vm_config(vmid, node):
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





def get_proxmox_vm_status(vmid, node):
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
        logging.error("Problem in get_proxmox_vm_status(" + str(vmid) + ") when getting VM status: " + str(e))
        return {"status": "error"}, 500


def get_vm_last_backup_date(vmid: int, node):
    try:
        backups = proxmox.nodes(node).storage("hosting_backup").content.get()
    except Exception as e:
        logging.error("Problem in accessing backups : " + str(e))
        return None
    
    backup_dates = []
    for r in backups:
        if vmid == r["vmid"]:
            try:
                backup_dates += [r["ctime"]]
            except Exception as e:
                logging.error("Problem in get_backup_vm_ctime("+str(vmid)+") when getting VM backups: " + str(e))
                return None

    if len(backup_dates) == 0:
        print("Error : no backup for VM "+ str(vmid))
        return 0

    return max(backup_dates)


# Select the next available ip address and set up in the proxmox firewall
def set_new_vm_ip(vmid, node):
    if configuration.ENVIRONMENT == "DEV":
        return "157.159.195.9"
    else:
        network = IPv4Network('157.159.195.0/24')
        reserved = {'157.159.195.1', '157.159.195.2', '157.159.195.3', '157.159.195.4', '157.159.195.5',
                        '157.159.195.6', '157.159.195.7', '157.159.195.8', '157.159.195.9',
                        '157.159.195.10'}
        hosts_iterator = (host for host in network.hosts() if str(host) not in reserved)
        ip = ""
        for host in hosts_iterator:
            if database.is_ip_available(host) == True:
                ip = host
                break
        if ip != "":
            return ip 
        else :
            return None # no ip available



def switch_autoreboot(vmid,node):
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
        vm_id_list = database.get_vm_list(user_id)
        ip_list = [] # ip of the user
        for vmid in vm_id_list:
            node,status = get_node_from_vm(vmid)
            if status != 200:
                return None
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
    user = database.get_user_list(user_id=username)
    if user is None:
        return {"freezeState" : "0"}, 200 # user doesn't exist so we fake the freezestatus
    try :
        freezeState = database.getFreezeState(username)
    except Exception as e :
        print(e)
        return {"freeztatus" : "unknown"}, 404 # User doesn't exist, we fake the freeze state to 0.0
    if freezeState is None: # We have to create the freeze state
        return check_update_cotisation(username)
    elif freezeState == "0.0":
        status = freezeState.split(".")[0]
        return {"freezeState" : status}, 200
    else:
        check_update_cotisation(username)
        freezeState = database.getFreezeState(username) # if expired with update in case of re-cotisation
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
        users = database.get_active_users()
        for user in users:
            try :
                status = check_update_cotisation(user)
                print("check_update_cotisation for user", user, " : ", status)
            except Exception as e:
                print("exception : ",e)
                pass
        database.session.commit()



"""func called by when cotisation is expired in case of recosition. For a userId it checks thecotisation, update the date if needed in the database. The send of email is done by Jenkins  (according to the frozen level (see wiki.minet.net))

    :param entry: userId : string

    :return: status code, {"status": "ok"} if the cotisation is ok, {"status": "expired"} if the cotisation is expired, {"error": "error message"} if there is an error
    :rtype: int, dict
"""
def check_update_cotisation(username, createEntry=False):
        
    print("check cotisation of", username)
    #headers = {"Authorization": req_headers}
    account, status = util.get_adh6_account(username)
    if (account is None):
        return {"error": "Impossible to retrieve the user info"}, 404
    print("Adh6 account", account)
    today =  date.today()
    if "ip" not in account: # Cotisation expired
        #print(username , "cotisation expired", membership.json())
        print(username , "cotisation expired (no ip)")
        
        #return expiredCotisation(username, userEmail) #, datetime.strptime(account["departureDate"], "%Y-%m-%d").date())
        
        status = database.getFreezeState(username)
        if status is None:
            status = '1'
            database.updateFreezeState(username, "1.0")
        return {"freezeState": status}, 200

    else :  # we check anyway if the departure date is inthe future
        #print(membership.json()["ip"])
        #print(membership.json()["departureDate"], end='\n\n')
        departureDate = datetime.strptime(account["departureDate"], "%Y-%m-%d").date()
        if departureDate < today: # Cotisation expired:
            print(username , "cotisation expired (departure date)")
            status = database.getFreezeState(username)
            if status is None:
                status = '1'
                database.updateFreezeState(username, "1.0")
            return {"freezeState": status}, 200

        else :
            print(username, "cotisation up to date")
            database.updateFreezeState(username, "0.0")
            return  {"freezeState": "0"}, 200  


def next_available_vmid():# determine the next available vmid from both db and proxmox
    next_vmid_db = 110
    is_vmid_available_prox = False 
    while next_vmid_db != None and not is_vmid_available_prox : # if next_vmid_db is None then there is no next vmid available and if is_vmid_available_prox = True then the next vmid is available in proxmox and in db
        next_vmid_db += 1
        next_vmid_db = database.getNextVmID(next_vmid_db)
       
        is_vmid_available_prox = is_vmid_available_cluster(next_vmid_db)
    return next_vmid_db


"""_summary_ : This function is called by the job to stop expired vm when the account freeze state is 2.x or 3.1
"""
def stop_expired_vm(app):
    print("Executing expired vm jobs ...")
    with app.app_context():    # Needs application context
        users = database.get_expired_users(minimumFreezeState=2)
        
        for user in users:
            print("Checking vm for user : ", user)
            userVms = database.get_vm_list(user_id=user)
            for vmid in userVms:
                node, _ = get_node_from_vm(vmid)
                status,_ = get_proxmox_vm_status(vmid, node)
                if status["status"] == "running":
                    print("Stopping vm", vmid , "which was running")
                    stop_vm(vmid, node)
            print("VMs stopped for user", user)

# Transfer the ownership of a vm to another user.
def transfer_ownership(vmid, newowner):
    if newowner == "" or newowner == None :
        return {"error": "No login given"}, 400
    
    user = database.get_user_list(user_id=newowner)
    if user == None: # We search it in ADH6
        account, status = util.get_adh6_account(newowner)
        if status != 200:
            return account, status
        if account is None:
            return {"error": "User not found"}, 404
        else:
            print("account", account)
            userid = account["username"]
            # We add the user in the database
            database.add_user(userid)
    else: 
        userid = newowner
        userVms = database.get_vm_list(user_id=userid)
        if len(userVms) >= 3:
            return {"error": "User already has 3 VMs"}, 400
    database.update_vm_userid(vmid, userid)
    ip  = database.get_vm_ip(vmid)
    database.add_ip_to_history(ip, vmid, userid)
    database.update_all_ip_dns_record(ip, userid)
    return {"status": "ok"}, 201
