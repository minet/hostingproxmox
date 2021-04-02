"""File used to configure hosting service"""
import os

# Proxmox host
PROXMOX_HOST = "192.168.104.16"

# Proxmox host
PROXMOX_USER = "root@pam"

# Proxmox host
PROXMOX_API_KEY = os.environ.get('PROXMOX_API_KEY')



# Proxmox host

PROXMOX_API_KEY_NAME = os.environ.get('PROXMOX_API_KEY_NAME')


# Database uri : "mysql://user:pass@dbhost/dbname"
#DATABASE_URI = "mysql://project:project@localhost/projet4"
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
