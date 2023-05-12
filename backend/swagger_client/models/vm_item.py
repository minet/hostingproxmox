# coding: utf-8

"""
    Proxmox

    Proxmox VPS provider  # noqa: E501

    OpenAPI spec version: 1.0.0
    Contact: webmaster@listes.minet.net
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class VmItem(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        "name": "str",
        "type": "str",
        "user": "str",
        "password": "str",
        "ssh_key": "str",
        "ip": "str",
        "cpu": "float",
        "ram": "float",
        "disk": "float",
        "autoreboot": "bool",
        "status": "str",
        "cpu_usage": "float",
        "ram_usage": "float",
        "uptime": "float",
        "created_on": "str",
    }

    attribute_map = {
        "name": "name",
        "type": "type",
        "user": "user",
        "password": "password",
        "ssh_key": "sshKey",
        "ip": "ip",
        "cpu": "cpu",
        "ram": "ram",
        "disk": "disk",
        "autoreboot": "autoreboot",
        "status": "status",
        "cpu_usage": "cpu_usage",
        "ram_usage": "ram_usage",
        "uptime": "uptime",
        "created_on": "created_on",
    }

    def __init__(
        self,
        name=None,
        type=None,
        user=None,
        password=None,
        ssh_key=None,
        ip=None,
        cpu=None,
        ram=None,
        disk=None,
        autoreboot=None,
        status=None,
        cpu_usage=None,
        ram_usage=None,
        uptime=None,
        created_on=None,
    ):  # noqa: E501
        """VmItem - a model defined in Swagger"""  # noqa: E501
        self._name = None
        self._type = None
        self._user = None
        self._password = None
        self._ssh_key = None
        self._ip = None
        self._cpu = None
        self._ram = None
        self._disk = None
        self._autoreboot = None
        self._status = None
        self._cpu_usage = None
        self._ram_usage = None
        self._uptime = None
        self._created_on = None
        self.discriminator = None
        if name is not None:
            self.name = name
        if type is not None:
            self.type = type
        if user is not None:
            self.user = user
        if password is not None:
            self.password = password
        if ssh_key is not None:
            self.ssh_key = ssh_key
        if ip is not None:
            self.ip = ip
        if cpu is not None:
            self.cpu = cpu
        if ram is not None:
            self.ram = ram
        if disk is not None:
            self.disk = disk
        if autoreboot is not None:
            self.autoreboot = autoreboot
        if status is not None:
            self.status = status
        if cpu_usage is not None:
            self.cpu_usage = cpu_usage
        if ram_usage is not None:
            self.ram_usage = ram_usage
        if uptime is not None:
            self.uptime = uptime
        if created_on is not None:
            self.created_on = created_on

    @property
    def name(self):
        """Gets the name of this VmItem.  # noqa: E501

        vm name  # noqa: E501

        :return: The name of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this VmItem.

        vm name  # noqa: E501

        :param name: The name of this VmItem.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def type(self):
        """Gets the type of this VmItem.  # noqa: E501

        type of vm  # noqa: E501

        :return: The type of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this VmItem.

        type of vm  # noqa: E501

        :param type: The type of this VmItem.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def user(self):
        """Gets the user of this VmItem.  # noqa: E501

        user of vm  # noqa: E501

        :return: The user of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this VmItem.

        user of vm  # noqa: E501

        :param user: The user of this VmItem.  # noqa: E501
        :type: str
        """

        self._user = user

    @property
    def password(self):
        """Gets the password of this VmItem.  # noqa: E501

        password of vm  # noqa: E501

        :return: The password of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this VmItem.

        password of vm  # noqa: E501

        :param password: The password of this VmItem.  # noqa: E501
        :type: str
        """

        self._password = password

    @property
    def ssh_key(self):
        """Gets the ssh_key of this VmItem.  # noqa: E501

        ssh pub key for auth  # noqa: E501

        :return: The ssh_key of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._ssh_key

    @ssh_key.setter
    def ssh_key(self, ssh_key):
        """Sets the ssh_key of this VmItem.

        ssh pub key for auth  # noqa: E501

        :param ssh_key: The ssh_key of this VmItem.  # noqa: E501
        :type: str
        """

        self._ssh_key = ssh_key

    @property
    def ip(self):
        """Gets the ip of this VmItem.  # noqa: E501

        vm public ip  # noqa: E501

        :return: The ip of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip):
        """Sets the ip of this VmItem.

        vm public ip  # noqa: E501

        :param ip: The ip of this VmItem.  # noqa: E501
        :type: str
        """

        self._ip = ip

    @property
    def cpu(self):
        """Gets the cpu of this VmItem.  # noqa: E501

        total VM's cpu  # noqa: E501

        :return: The cpu of this VmItem.  # noqa: E501
        :rtype: float
        """
        return self._cpu

    @cpu.setter
    def cpu(self, cpu):
        """Sets the cpu of this VmItem.

        total VM's cpu  # noqa: E501

        :param cpu: The cpu of this VmItem.  # noqa: E501
        :type: float
        """

        self._cpu = cpu

    @property
    def ram(self):
        """Gets the ram of this VmItem.  # noqa: E501

        total VM's ram in MiO  # noqa: E501

        :return: The ram of this VmItem.  # noqa: E501
        :rtype: float
        """
        return self._ram

    @ram.setter
    def ram(self, ram):
        """Sets the ram of this VmItem.

        total VM's ram in MiO  # noqa: E501

        :param ram: The ram of this VmItem.  # noqa: E501
        :type: float
        """

        self._ram = ram

    @property
    def disk(self):
        """Gets the disk of this VmItem.  # noqa: E501

        total VM's disk size in GiO  # noqa: E501

        :return: The disk of this VmItem.  # noqa: E501
        :rtype: float
        """
        return self._disk

    @disk.setter
    def disk(self, disk):
        """Sets the disk of this VmItem.

        total VM's disk size in GiO  # noqa: E501

        :param disk: The disk of this VmItem.  # noqa: E501
        :type: float
        """

        self._disk = disk

    @property
    def autoreboot(self):
        """Gets the autoreboot of this VmItem.  # noqa: E501

        vm autoreboot value  # noqa: E501

        :return: The autoreboot of this VmItem.  # noqa: E501
        :rtype: bool
        """
        return self._autoreboot

    @autoreboot.setter
    def autoreboot(self, autoreboot):
        """Sets the autoreboot of this VmItem.

        vm autoreboot value  # noqa: E501

        :param autoreboot: The autoreboot of this VmItem.  # noqa: E501
        :type: bool
        """

        self._autoreboot = autoreboot

    @property
    def status(self):
        """Gets the status of this VmItem.  # noqa: E501

        vm status  # noqa: E501

        :return: The status of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this VmItem.

        vm status  # noqa: E501

        :param status: The status of this VmItem.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def cpu_usage(self):
        """Gets the cpu_usage of this VmItem.  # noqa: E501

        cpu usage in percent  # noqa: E501

        :return: The cpu_usage of this VmItem.  # noqa: E501
        :rtype: float
        """
        return self._cpu_usage

    @cpu_usage.setter
    def cpu_usage(self, cpu_usage):
        """Sets the cpu_usage of this VmItem.

        cpu usage in percent  # noqa: E501

        :param cpu_usage: The cpu_usage of this VmItem.  # noqa: E501
        :type: float
        """

        self._cpu_usage = cpu_usage

    @property
    def ram_usage(self):
        """Gets the ram_usage of this VmItem.  # noqa: E501

        ram usage in percent  # noqa: E501

        :return: The ram_usage of this VmItem.  # noqa: E501
        :rtype: float
        """
        return self._ram_usage

    @ram_usage.setter
    def ram_usage(self, ram_usage):
        """Sets the ram_usage of this VmItem.

        ram usage in percent  # noqa: E501

        :param ram_usage: The ram_usage of this VmItem.  # noqa: E501
        :type: float
        """

        self._ram_usage = ram_usage

    @property
    def uptime(self):
        """Gets the uptime of this VmItem.  # noqa: E501

        VM's uptime in sec  # noqa: E501

        :return: The uptime of this VmItem.  # noqa: E501
        :rtype: float
        """
        return self._uptime

    @uptime.setter
    def uptime(self, uptime):
        """Sets the uptime of this VmItem.

        VM's uptime in sec  # noqa: E501

        :param uptime: The uptime of this VmItem.  # noqa: E501
        :type: float
        """

        self._uptime = uptime

    @property
    def created_on(self):
        """Gets the created_on of this VmItem.  # noqa: E501

        creation date of the VM  # noqa: E501

        :return: The created_on of this VmItem.  # noqa: E501
        :rtype: str
        """
        return self._created_on

    @created_on.setter
    def created_on(self, created_on):
        """Sets the created_on of this VmItem.

        creation date of the VM  # noqa: E501

        :param created_on: The created_on of this VmItem.  # noqa: E501
        :type: str
        """

        self._created_on = created_on

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(VmItem, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, VmItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
