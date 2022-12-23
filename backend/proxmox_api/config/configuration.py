"""File used to configure hosting service"""
import os
import logging

# Logging info
LOG_FILE_NAME = "backend.log"
LOG_LEVEL = logging.DEBUG

# Ldap dn for hosting admin
ADMIN_DN = 'cn=cluster-hosting,ou=groups,dc=minet,dc=net'

# Proxmox host
PROXMOX_HOST = "192.168.104.7"

# Proxmox host
PROXMOX_USER = "root@pam"

# Proxmox host
PROXMOX_API_KEY = os.environ.get('PROXMOX_API_KEY')

# VM number limit by user and total
LIMIT_BY_USER = 3
TOTAL_VM_LIMIT = 120

# Proxmox host

PROXMOX_API_KEY_NAME = os.environ.get('PROXMOX_API_KEY_NAME')
ADH6_API_KEY = os.environ.get('ADH6_API_KEY')

# Database uri : "mysql://user:pass@dbhost/dbname"
"""Be sure to set "set global log_bin_trust_function_creators=1"; in the database if mysql"""


if os.environ.get('ENVIRONMENT') == 'DEV':
    ENV = "DEV"
    #DATABASE_URI = os.environ.get('PROXMOX_BACK_DB_DEV')
    DATABASE_URI = 'sqlite:///proxmox_dev.db'
else :
    ENV = "PROD"
    DATABASE_URI = os.environ.get('PROXMOX_BACK_DB')



# Not used for now
MAX_USER_CPU = ""
MAX_USER_DISK = ""
MAX_USER_RAM = ""
##

# DDNS keyring secret
KEYRING_DNS_SECRET = os.environ.get('KEYRING_DNS_SECRET')



# DDNS keyring name
KEYRING_DNS_NAME = 'updateddns.'

# Domain for hosting service
HOSTING_DOMAIN = 'h.minet.net'

# TTL in DNS entry
DNS_ENTRY_TTL = 14400

# Main DNS server ip
MAIN_DNS_SERVER_IP = "192.168.104.28"



VM_CREATION_STATUS_JSON = "proxmox_api/config/vm_creation_status.json" # json file of all vm creating and there status. If an error occur during the creation, the vm is deleted and the error code is kepts until the user get it. This is a informationnal dictionnary and cannot be trust at 100%.