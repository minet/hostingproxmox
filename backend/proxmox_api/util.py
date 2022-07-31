import datetime

import six
import typing
import re
import json
import proxmox_api.config.configuration as  config 

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
    special = "[`!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~]";
    upper = "[A-Z]";
    number = "[0-9]";
    # Return true if and only if there are at least 12 char, 1 spec char, 1 uppercase letter and 1 lowercase letter
    return len(password) >= 12 and re.search(special, password) is not  None  and re.search(upper, password) is not None and  re.search(number, password) is not None


"""Check if the user ssh key has a correct format

    :param key: the ssh key to check

    :return: True if the ssh key has a correct format
    :rtype: bool
"""
def check_ssh_key(key:str) -> bool:
    return not not re.search("^ssh.[a-zA-Z0-9]* [a-zA-Z0-9[()[\]{}+*\/%$&#@=:?]*", key)



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
    allowed = "^[a-zA-Z0-9]*$"; 
    return entry != "" and re.search(allowed, entry) and entry not in forbidden_entries



"""Return the vm creation status retrieved in the json file
    Possible status are created, creating and error
    If status == error,  error code and errorMessage explain the error
    If not, its are None

    :param entry: vmid of the vm creating

    :return: (status, httpErrorCode, errorMessage)
    :rtype:  Tuple[str, str, str]
"""
def vm_creation_status(vmid) :
    with open(config.VM_CREATION_STATUS_JSON) as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    try : 
        vm = jsonObject[str(vmid)]
        if vm == None : 
            return None 
        else: 
            status = vm["status"]
            if status == "error":
                return (status, vm["httpErrorCode"], vm["errorMessage"])
            elif status == "creating" or status == "created": 
                return (status, None, None)
            else: 
                return ("error", 500, "Impossible to retrieve the status of the vm")
    except : 
        return None




"""Update the vm creation status json file

    :param entry: 
        - vmid : the id of the vm creating
        - message : message associated to the creation
        - errorCode (optionnal): httpError code if relevant 
        - deleteEntry (optionnal): if True, the entry is deleted

    :return: True if success else False
    :rtype: bool
"""
def update_vm_status(vmid, message, errorCode = 0, deleteEntry = False) -> bool:
    with open(config.VM_CREATION_STATUS_JSON) as jsonFile:
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
        return True 
    except Exception as e: 
        print("An error occured while updating the vm creation status dict : " , e)
        return False
