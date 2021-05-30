"""File used to configure hosting service"""
import os
import logging

# Logging info
LOG_FILE_NAME = "backend.log"
LOG_LEVEL = logging.DEBUG

# Ldap dn for hosting admin
ADMIN_DN = 'cn=hosting,ou=groups,dc=minet,dc=net'

# Proxmox host
PROXMOX_HOST = "192.168.104.16"

# Proxmox host
PROXMOX_USER = "root@pam"

# Proxmox host
PROXMOX_API_KEY = os.environ.get('PROXMOX_API_KEY')

# VM number limit by user and total
LIMIT_BY_USER = 3
TOTAL_VM_LIMIT = 120

# Proxmox host

PROXMOX_API_KEY_NAME = os.environ.get('PROXMOX_API_KEY_NAME')


# Database uri : "mysql://user:pass@dbhost/dbname"
"""Be sure to set "set global log_bin_trust_function_creators=1"; in the database if mysql"""

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
MAIN_DNS_SERVER_IP = "192.168.104.17"
