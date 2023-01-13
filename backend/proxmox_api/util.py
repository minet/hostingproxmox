import datetime
import six
import typing
import re
import json
import requests
import connexion
from flask_apscheduler import APScheduler
from flask_cors import CORS
import proxmox_api.config.configuration as  config 
import proxmox_api.config.configuration as config
from proxmox_api import encoder


def _deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if klass in six.integer_types or klass in (float, str, bool):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif type(klass) == typing.GenericMeta:
        if klass.__extra__ == list:
            return _deserialize_list(data, klass.__args__[0])
        if klass.__extra__ == dict:
            return _deserialize_dict(data, klass.__args__[1])
    else:
        return deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = six.u(data)
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return a original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.swagger_types:
        return data

    for attr, attr_type in six.iteritems(instance.swagger_types):
        if data is not None \
                and instance.attribute_map[attr] in data \
                and isinstance(data, (list, dict)):
            value = data[instance.attribute_map[attr]]
            setattr(instance, attr, _deserialize(value, attr_type))

    return instance


def _deserialize_list(data, boxed_type):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type)
            for sub_data in data]


def _deserialize_dict(data, boxed_type):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type)
            for k, v in six.iteritems(data)}


"""Check if the user password is strong enough to be used

    :param password: the password to check

    :return: True if the password is strong enough, false if not
    :rtype: bool
"""
def check_password_strength(password:str) -> bool:
    special = "[`!@#$%^&*()_+-=[\]{};':\"\\|,.<>/?~]"
    upper = "[A-Z]"
    number = "[0-9]"
    # Return true if and only if there are at least 12 char, 1 spec char, 1 uppercase letter and 1 lowercase letter
    return len(password) >= 12 and re.search(special, password) is not  None  and re.search(upper, password) is not None and  re.search(number, password) is not None


"""Check if the user ssh key has a correct format

    :param key: the ssh key to check

    :return: True if the ssh key has a correct format
    :rtype: bool
"""
def check_ssh_key(key:str) -> bool:
    return not not re.search("^[a-zA-Z0-9[()[\].{\-}_+*""\/%$&#@=:?]* [a-zA-Z0-9[()[\].{\-}_+*""\/%$&#@=:?]* [a-zA-Z0-9[()[\].{\-}_+*""\/%$&#@=:?]*", key)



"""Check if the username is acceptable

    :param username: the username to check

    :return: True if the username is acceptable
    :rtype: bool
"""
def check_username(username:str) -> bool:
    return username != "root" and username != ""



"""Check if the dns entry is acceptable

    :param entry: the entry to check

    :return: True if the entry is acceptable
    :rtype: bool
"""
def check_dns_entry(entry:str) -> bool:
    forbidden_entries = ["armes", "arme", "fuck", "porn", "porno", "weapon", "weapons", "pornographie", "amazon", "sex", "sexe", "attack", "hack", "attaque", "hacker", "hacking", "pornhub", "xxx", "store", "hosting", "adh6"]
    allowed = "^[a-zA-Z0-9]*$"
    return entry != "" and re.search(allowed, entry) and entry not in forbidden_entries



"""Return the vm creation state retrieved in the json file
    Possible status are created, creating, deleting, deleted and error
    If status == error,  error code and errorMessage explain the error
    If not, its are None

    :param entry: vmid of the vm creating

    :return: (status, httpErrorCode, errorMessage)
    :rtype:  Tuple[str, str, str]
"""
def get_vm_state(vmid) :
    with open(config.VM_CREATION_STATUS_JSON, mode='r') as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    try :
        vm = jsonObject[str(vmid)]
        print(vm)
        if vm is None :
            return None
        else: 
            status = vm["status"]
            if status == "error":
                return (status, vm["httpErrorCode"], vm["errorMessage"])
            elif status == "creating" or status == "created" or status == "deleting" or status == "deleted" :
                return (status, None, None)
            else:
                return ("error", 500, "Impossible to retrieve the status of the vm")
    except :
        return None







"""Update the vm creation state json file

    :param entry: 
        - vmid : the id of the vm creating
        - message : message associated to the creation
        - errorCode (optionnal): httpError code if relevant 
        - deleteEntry (optionnal): if True, the entry is deleted

    :return: True if success else False
    :rtype: bool
"""
def update_vm_state(vmid, message, errorCode = 0, deleteEntry = False) -> bool:
    with open(config.VM_CREATION_STATUS_JSON, mode='r') as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()

    try :
        if deleteEntry :
            jsonObject.pop(str(vmid))
        else :
           jsonObject[vmid] = {}
           if not errorCode: # not 0 = 1 = True
                jsonObject[vmid]["status"] = message
           else:
                jsonObject[vmid]["status"] = "error"
                jsonObject[vmid]["httpErrorCode"] = str(errorCode) 
                jsonObject[vmid]["errorMessage"] = message
        with open(config.VM_CREATION_STATUS_JSON, "w") as outfile:
            json.dump(jsonObject, outfile)
            outfile.close()
        return True
    except Exception as e:
        print("An error occured while updating the vm creation status dict : " , e)
        return False


"""generate the main freeze state (0,1,2 or 3) and the nb of  notification sent  based on the departure date. 

    :param entry: 
        - departure date as a datetime object
        -lastNotificationDate : date of the last notification (None if no relevant)
        - Old freeze state : string

    :return: freeze state (0,1,2 or 3), ont
    :rtype: tuple
"""
def generateNewFreezeState(freezeState) :# return the freeze state of the user based on the last notification date and departure date
    if freezeState is None : 
        return (1,1)
    status, nbNotif = int(freezeState.split(".")[0]), int(freezeState.split(".")[1])
    if status == 0 :
        return (1, 1)
    else :
        newFreezeStatus = status + nbNotif//5 # while we don't have send 4 notifications, we don't change the status
        nbNotif %= 5
        return (newFreezeStatus, nbNotif)


    

def create_app():

    app = connexion.App(__name__, specification_dir='./swagger/')

    app.app.json_encoder = encoder.JSONEncoder

    app.app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app


def check_cas_token(headers):
    #if config.ENV == "DEV":
    #    if headers["Fake-User"] == "admin":
    #        return 200, {'sub': 'fake-admin', "attributes" : {"memberOf" : 'cn=cluster-hosting,ou=groups,dc=minet,dc=net'}}
    #    else :
    #        return 200, {'sub': headers["Fake-User"]}
    #elif config.ENV == "PROD":
    autorization = {"Authorization": headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=autorization)
    print("return =", r.json())
    return r.status_code, r.json()
    


# heck_adh6_membership
def get_adh6_account(headers, userId):
    response = requests.get("https://adh6.minet.net/api/member/"+str(userId), headers=headers) # memership info
    return response.json()

def adh6_search_user(username, headers):
    response = requests.get("https://adh6.minet.net/api/member/?limit=25&terms="+str(username), headers=headers) # [id], from ADH6 
    return None if response is None else response.json()
