""" Here you can find all DDNS related functions """

import dns.update
import dns.query
import dns.reversename
import dns.rdatatype
import dns.tsigkeyring
from proxmox_api.config import configuration

keyring = dns.tsigkeyring.from_text(
    {configuration.KEYRING_DNS_NAME: ("HMAC-SHA512", configuration.KEYRING_DNS_SECRET)}
)


def create_entry(entry, ip_add):
    """ Add a record with ddns protocole in configuration.MAIN_DNS_SERVER_IP DNS server """
    dns_domain = "%s." % configuration.HOSTING_DOMAIN
    datatype = dns.rdatatype.from_text("A")
    rdata = dns.rdata.from_text(dns.rdataclass.IN, datatype, ip_add)
    update = dns.update.Update(dns_domain, keyring=keyring)
    update.absent(entry)
    update.add(entry, configuration.DNS_ENTRY_TTL, rdata)
    response = dns.query.tcp(update, configuration.MAIN_DNS_SERVER_IP, timeout=5)
    print(response.rcode())
    if response.rcode() == 0:
        return {"dns": "entry created"}, 201
    if response.rcode() == 6:
        return {"dns": "entry already exists"}, 405
    return {"dns": "error occured"}, 500




def delete_dns_record(entry):
    """ Delete a record with ddns protocole in configuration.MAIN_DNS_SERVER_IP DNS server """
    dns_domain = "%s." % configuration.HOSTING_DOMAIN
    update = dns.update.Update(dns_domain, keyring=keyring)
    update.present(entry)
    update.delete(entry)
    response = dns.query.tcp(update, configuration.MAIN_DNS_SERVER_IP, timeout=5)
    if response.rcode() == 0:
        return {"dns": "entry deleted"}, 201
    if response.rcode() == 3:
        return {"dns": "entry does not exist"}, 405

    return {"dns": "error occured"}, 500
