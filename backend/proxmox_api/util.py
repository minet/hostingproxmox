import datetime
import six
import typing
import re
import json
import requests
import connexion
import tempfile
import subprocess
import proxmox_api.config.configuration as  config 
import proxmox_api.config.configuration as config
from proxmox_api import encoder
from proxmox_api.db.db_models import db
from email.message import EmailMessage
import smtplib


if not bool(config.ADH6_API_KEY):
    raise Exception("NO ADH6 API KEY GIVEN")


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


"""
Translation of the following Perl script originating from proxmox's pve-common package:
https://github.com/proxmox/pve-common/blob/12a0ec1888e4c423dbe890b65460a703afb91c47/src/PVE/Tools.pm#L1667

sub validate_ssh_public_keys {
    my ($raw) = @_;
    my @lines = split(/\n/, $raw);

    foreach my $line (@lines) {
	next if $line =~ m/^\s*$/;
	eval {
	    my ($filename, $handle) = tempfile_contents($line);
	    run_command(["ssh-keygen", "-l", "-f", $filename],
			outfunc => sub {}, errfunc => sub {});
	};
	die "SSH public key validation error\n" if $@;
    }
}

"""
def check_ssh_key(raw: str) -> bool:
    lines = raw.split("\n")
    for line in lines:
        if re.match(r"^\s*$", line):
            continue
        try:
            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(line.encode())
                tmp_file.flush()
                subprocess.run(["ssh-keygen", "-l", "-f", tmp_file.name], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               check=True)
        except subprocess.CalledProcessError:
            return False
    return True



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
    allowed = "^[a-zA-Z0-9-._]*$"
    return entry != "" and re.search(allowed, entry) and entry not in forbidden_entries






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
    db.init_app(app.app)  

    return app


def check_cas_token(headers):
    #if config.ENV == "TEST":
    #    if headers["Fake-User"] == "admin":
    #        return 200, {'sub': 'fake-admin', "attributes" : {"memberOf" : 'cn=cluster-hosting,ou=groups,dc=minet,dc=net'}}
    #    else :
    #        return 200, {'sub': headers["Fake-User"]}
    #elif config.ENV == "PROD":
    autorization = {"Authorization": headers["Authorization"]}
    r = requests.get("https://cas.minet.net/oidc/profile", headers=autorization)
    return r.status_code, r.json()
    



def get_adh6_account(username):
    headers = {"X-API-KEY": config.ADH6_API_KEY}
    #print("https://adh6.minet.net/api/member/?limit=25&filter%5Busername%5D="+str(username)+"&only=id,username")
    userInfoJson = adh6_search_user(username, headers)
    if userInfoJson is None or userInfoJson  == []: # not found
            print("ERROR : the user " , username , " failed to be retrieved :" , userInfoJson)
            return {"error" : "the user " + username + " failed to be retrieved"}, 404
    else : 
        account = None
        for id in userInfoJson:
            accountJson = requests.get("https://adh6.minet.net/api/member/"+str(id), headers=headers) # memership info
            tmp_account = accountJson.json()
            if tmp_account["username"].lower() == username.lower():
                account = tmp_account
        return account, 200

def adh6_search_user(username, headers):
    response = requests.get("https://adh6.minet.net/api/member/?limit=25&terms="+str(username), headers=headers) # [id], from ADH6 
    return None if response is None else response.json()


# Subscribe on adh6 a user to the hosting mailing list
def subscribe_to_hosting_ML(username):
    print("Subscribe to hosting ML : " + username)
    headers = {"X-API-KEY": config.ADH6_API_KEY}
    userInfoJson = adh6_search_user(username, headers)
    if userInfoJson is None or userInfoJson  == []: # not found
        if "-" in username:
            print("ERROR : the user " + username + " is not found in ADH6. Try with", end='')
            new_username = username.replace("-","_") # hosting replace by default _ with -. So we try if not found
            print("'"+new_username+"'")
            return get_adh6_account(new_username)
            
        elif "_" in username: # same
            print("ERROR : the user " + username + " is not found in ADH6. Try with", end='')
            new_username = username.replace("_",".").strip() # hosting replace by default _ with -. So we try if not found
            print("'"+new_username+"'")
            return get_adh6_account(new_username)
        else :
            print("ERROR : the user " , username , " failed to be retrieved :" , userInfoJson)
            return {"error" : "the user " + username + " failed to be retrieved"}, 404
    else : 
        for id in userInfoJson:
            accountJson = requests.get("https://adh6.minet.net/api/member/"+str(id), headers=headers) # memership info
            tmp_account = accountJson.json()
            if tmp_account["username"].lower() == username.lower():
                current_ML_status = tmp_account["mailinglist"]
                new_ML_status = int(str(bin(current_ML_status))[:-2] + "1" + str(bin(current_ML_status))[-1], 2) # Add 1 to the bit before the last one, no matter the old value
                headers["Content-Type"] = "application/json"
                response  = requests.put("https://adh6.minet.net/api/mailinglist/member/"+str(id), headers=headers, data=json.dumps({"value": new_ML_status}))
                status = "OK"
                if response.status_code != 200:
                    status = "An unknown error occured"
                return status, response.status_code
    
    return {"error" : "the user " + username + " failed to be retrieved"}, 404

def sendMailBureau(htmlbody, username):
    msg = EmailMessage()
    msg['From'] = "hosting-noreply@minet.net"
    msg['To'] = "bureau@listes.minet.net"
    # msg['Bcc'] = "archive_expired_cotisation_hosting@listes.minet.net"
    msg['subject'] = f"[Hosting] : {username} veut créer un nom de domaine !"
    msg.add_header('Content-Type','text/html')
    msg.set_payload(htmlbody.encode('utf-8'))
    server = smtplib.SMTP("192.168.102.18:25")
    server.send_message(msg)
    server.set_debuglevel(1)
    server.quit()
    print("OK email")
    return 0



def sendMailAdherent(usermail: str, htmlbody: str, entry: str, accepted: bool):
    msg = EmailMessage()
    msg['From'] = "hosting-noreply@minet.net"
    print(usermail)
    msg['To'] = usermail
    # msg['Bcc'] = "archive_expired_cotisation_hosting@listes.minet.net"
    if accepted:
        msg['subject'] = f"[Hosting] : {entry} a été accepté comme nom de domaine!"
    else:
        msg['subject'] = f"[Hosting] : {entry} a été refusé comme nom de domaine!"
        
    msg.add_header('Content-Type','text/html')
    msg.set_payload(htmlbody.encode('utf-8'))
    server = smtplib.SMTP("192.168.102.18:25")
    server.send_message(msg)
    server.set_debuglevel(1)
    server.quit()
    print("OK email")
    return 0

def mailHTMLBureau(username, entry, ip):
    
    header="""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<style>
body{
    font-family: Helvetica, sans-serif;
    font-size: 14px;
    font-color:black;
}
</style>""".replace('\n', ' ').replace('\r', ' ')
    msg = f"""
<body>
    &#128680; Une personne souhaite ajouter une nouvelle entrée DNS sur hosting : {username} qui veut mettre en ligne {entry} pour l'IP {ip}.<br>
    Un admin Hosting doit la valider sur <a href="https://hosting.minet.net">hosting.minet.net</a>
</body></html>
        """.replace('\n', ' ').replace('\r', ' ')
    return header+msg

def mailHTMLAdherent(username: str, entry: str, ip: str, accepted:str):
    
    header="""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<style>
body{
    font-family: Helvetica, sans-serif;
    font-size: 14px;
    font-color:black;
}
</style>""".replace('\n', ' ').replace('\r', ' ')
    msg = f"""
<body>

    Bonjour {username}, <br> 
    Ton entrée DNS <strong>{entry}</strong> pour ta machine d'IP <strong>{ip}</strong> a été {accepted} par un admin sur <a href="https://hosting.minet.net">hosting</a>.<br>
    Cordialement,<br>
    <table style="font-size: medium; font-family: Arial; background:white; width:vw;" class="sc-gPEVay eQYmiW" cellspacing="0" cellpadding="0"><tbody><tr><td><table style="font-size: medium; font-family: Arial;" class="sc-gPEVay eQYmiW" cellspacing="0" cellpadding="0"><tbody><tr><td style="vertical-align: middle;" width="150"><span style="margin-right: 20px; display: block;" class="sc-kgAjT cuzzPp"><img src="https://www.minet.net/res/img/minet.png" role="presentation" style="max-width: 130px;" class="sc-cHGsZl bHiaRe" width="130"></span></td><td style="vertical-align: middle;"><font color="#000000" size="4"><span style="caret-color: rgb(0, 0, 0);"><b>L'équipe MINET</b></span></font><p color="#000000" font-size="medium" style="margin: 0px; color: rgb(0, 0, 0); font-size: 14px; line-height: 22px;" class="sc-fMiknA bxZCMx"><span></span></p><p color="#000000" font-size="medium" style="margin: 0px; font-weight: 500; color: rgb(0, 0, 0); font-size: 14px; line-height: 22px;" class="sc-dVhcbM fghLuF"><span></span></p></td><td width="30"><div style="width: 30px;"></div></td><td color="#6fa3e8" direction="vertical" style="width: 1px; border-bottom: medium none; border-left: 1px solid rgb(111, 163, 232);" class="sc-jhAzac hmXDXQ" width="1"></td><td width="30"><div style="width: 30px;"></div></td><td style="vertical-align: middle;"><table style="font-size: medium; font-family: Arial;" class="sc-gPEVay eQYmiW" cellspacing="0" cellpadding="0"><tbody><tr><td style="padding: 0px;"><a href="https://tickets.minet.net" color="#000000" style="text-decoration: none; color: rgb(0, 0, 0); font-size: 12px;" class="sc-gipzik iyhjGb"><span style="margin-left:1px; font-family: Arial;">&#128735; tickets.minet.net</span></a></td></tr><tr><td style="padding: 0px;"><a href="//www.minet.net" color="#000000" style="text-decoration: none; color: rgb(0, 0, 0); font-size: 12px;" class="sc-gipzik iyhjGb"><span style="margin-left:1px; font-family: Arial;">&#127760;  www.minet.net</span></a></td></tr><tr style="vertical-align: middle;" height="25"><td style="padding: 0px;"><span color="#000000" style="font-size: 12px; color: rgb(0, 0, 0);" class="sc-csuQGl CQhxV"><span style="margin-left:1px; font-family: Arial;"> &#128235;  9 rue Charles Fourier, 91000, Evry</span></span></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td></td></tr><tr><td></td></tr></tbody></table>
    </body></html>
        """.replace('\n', ' ').replace('\r', ' ')
    return header+msg
    