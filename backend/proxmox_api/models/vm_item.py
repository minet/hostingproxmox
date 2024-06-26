# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from proxmox_api.models.base_model_ import Model
from proxmox_api import util


class VmItem(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, name: str=None, type: str=None, user: str=None, password: str=None, ssh: bool=None, ssh_key: str=None, ip: str=None, cpu: float=None, ram: float=None, disk: float=None, status: str=None, cpu_usage: float=None, ram_usage: float=None, uptime: float=None, last_backup_date: float=None, created_on: str=None):  # noqa: E501
        """VmItem - a model defined in Swagger

        :param name: The name of this VmItem.  # noqa: E501
        :type name: str
        :param type: The type of this VmItem.  # noqa: E501
        :type type: str
        :param user: The user of this VmItem.  # noqa: E501
        :type user: str
        :param password: The password of this VmItem.  # noqa: E501
        :type password: str
        :param ssh: The ssh of this VmItem.  # noqa: E501
        :type ssh: bool
        :param ssh_key: The ssh_key of this VmItem.  # noqa: E501
        :type ssh_key: str
        :param ip: The ip of this VmItem.  # noqa: E501
        :type ip: str
        :param cpu: The cpu of this VmItem.  # noqa: E501
        :type cpu: float
        :param ram: The ram of this VmItem.  # noqa: E501
        :type ram: float
        :param disk: The disk of this VmItem.  # noqa: E501
        :type disk: float
        :param status: The status of this VmItem.  # noqa: E501
        :type status: str
        :param cpu_usage: The cpu_usage of this VmItem.  # noqa: E501
        :type cpu_usage: float
        :param ram_usage: The ram_usage of this VmItem.  # noqa: E501
        :type ram_usage: float
        :param uptime: The uptime of this VmItem.  # noqa: E501
        :type uptime: float
        :param last_backup_date: The last backup date of this VmItem.  # noqa: E501
        :type last_backup_date: float
        :param created_on: The created_on of this VmItem.  # noqa: E501
        :type created_on: str
        """
        self.swagger_types = {
            'name': str,
            'type': str,
            'user': str,
            'password': str,
            'ssh': bool,
            'ssh_key': str,
            'ip': str,
            'cpu': float,
            'ram': float,
            'disk': float,
            'status': str,
            'cpu_usage': float,
            'ram_usage': float,
            'uptime': float,
            'last_backup_date': float,
            'created_on': str
        }

        self.attribute_map = {
            'name': 'name',
            'type': 'type',
            'user': 'user',
            'password': 'password',
            'ssh': 'ssh',
            'ssh_key': 'sshKey',
            'ip': 'ip',
            'cpu': 'cpu',
            'ram': 'ram',
            'disk': 'disk',
            'status': 'status',
            'cpu_usage': 'cpu_usage',
            'ram_usage': 'ram_usage',
            'uptime': 'uptime',
            'last_backup_date': 'last_backup_date',
            'created_on': 'created_on'
        }
        self._name = name
        self._type = type
        self._user = user
        self._password = password
        self._ssh = ssh
        self._ssh_key = ssh_key
        self._ip = ip
        self._cpu = cpu
        self._ram = ram
        self._disk = disk
        self._status = status
        self._cpu_usage = cpu_usage
        self._ram_usage = ram_usage
        self._uptime = uptime
        self._last_backup_date = last_backup_date
        self._created_on = created_on

    @classmethod
    def from_dict(cls, dikt) -> 'VmItem':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The VmItem of this VmItem.  # noqa: E501
        :rtype: VmItem
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self) -> str:
        """Gets the name of this VmItem.

        vm name  # noqa: E501

        :return: The name of this VmItem.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this VmItem.

        vm name  # noqa: E501

        :param name: The name of this VmItem.
        :type name: str
        """

        self._name = name

    @property
    def type(self) -> str:
        """Gets the type of this VmItem.

        type of vm  # noqa: E501

        :return: The type of this VmItem.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this VmItem.

        type of vm  # noqa: E501

        :param type: The type of this VmItem.
        :type type: str
        """

        self._type = type

    @property
    def user(self) -> str:
        """Gets the user of this VmItem.

        user of vm  # noqa: E501

        :return: The user of this VmItem.
        :rtype: str
        """
        return self._user

    @user.setter
    def user(self, user: str):
        """Sets the user of this VmItem.

        user of vm  # noqa: E501

        :param user: The user of this VmItem.
        :type user: str
        """

        self._user = user

    @property
    def password(self) -> str:
        """Gets the password of this VmItem.

        password of vm  # noqa: E501

        :return: The password of this VmItem.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password: str):
        """Sets the password of this VmItem.

        password of vm  # noqa: E501

        :param password: The password of this VmItem.
        :type password: str
        """

        self._password = password

    @property
    def ssh(self) -> bool:
        """Gets the ssh of this VmItem.

        ssh key auth  # noqa: E501

        :return: The ssh of this VmItem.
        :rtype: bool
        """
        return self._ssh

    @ssh.setter
    def ssh(self, ssh: bool):
        """Sets the ssh of this VmItem.

        ssh key auth  # noqa: E501

        :param ssh: The ssh of this VmItem.
        :type ssh: bool
        """

        self._ssh = ssh

    @property
    def ssh_key(self) -> str:
        """Gets the ssh_key of this VmItem.

        ssh pub key for auth  # noqa: E501

        :return: The ssh_key of this VmItem.
        :rtype: str
        """
        return self._ssh_key

    @ssh_key.setter
    def ssh_key(self, ssh_key: str):
        """Sets the ssh_key of this VmItem.

        ssh pub key for auth  # noqa: E501

        :param ssh_key: The ssh_key of this VmItem.
        :type ssh_key: str
        """

        self._ssh_key = ssh_key

    @property
    def ip(self) -> str:
        """Gets the ip of this VmItem.

        vm public ip  # noqa: E501

        :return: The ip of this VmItem.
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip: str):
        """Sets the ip of this VmItem.

        vm public ip  # noqa: E501

        :param ip: The ip of this VmItem.
        :type ip: str
        """

        self._ip = ip

    @property
    def cpu(self) -> float:
        """Gets the cpu of this VmItem.

        total VM's cpu  # noqa: E501

        :return: The cpu of this VmItem.
        :rtype: float
        """
        return self._cpu

    @cpu.setter
    def cpu(self, cpu: float):
        """Sets the cpu of this VmItem.

        total VM's cpu  # noqa: E501

        :param cpu: The cpu of this VmItem.
        :type cpu: float
        """

        self._cpu = cpu

    @property
    def ram(self) -> float:
        """Gets the ram of this VmItem.

        total VM's ram in MiO  # noqa: E501

        :return: The ram of this VmItem.
        :rtype: float
        """
        return self._ram

    @ram.setter
    def ram(self, ram: float):
        """Sets the ram of this VmItem.

        total VM's ram in MiO  # noqa: E501

        :param ram: The ram of this VmItem.
        :type ram: float
        """

        self._ram = ram

    @property
    def disk(self) -> float:
        """Gets the disk of this VmItem.

        total VM's disk size in GiO  # noqa: E501

        :return: The disk of this VmItem.
        :rtype: float
        """
        return self._disk

    @disk.setter
    def disk(self, disk: float):
        """Sets the disk of this VmItem.

        total VM's disk size in GiO  # noqa: E501

        :param disk: The disk of this VmItem.
        :type disk: float
        """

        self._disk = disk

    @property
    def status(self) -> str:
        """Gets the status of this VmItem.

        vm status  # noqa: E501

        :return: The status of this VmItem.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status: str):
        """Sets the status of this VmItem.

        vm status  # noqa: E501

        :param status: The status of this VmItem.
        :type status: str
        """

        self._status = status

    @property
    def cpu_usage(self) -> float:
        """Gets the cpu_usage of this VmItem.

        cpu usage in percent  # noqa: E501

        :return: The cpu_usage of this VmItem.
        :rtype: float
        """
        return self._cpu_usage

    @cpu_usage.setter
    def cpu_usage(self, cpu_usage: float):
        """Sets the cpu_usage of this VmItem.

        cpu usage in percent  # noqa: E501

        :param cpu_usage: The cpu_usage of this VmItem.
        :type cpu_usage: float
        """

        self._cpu_usage = cpu_usage

    @property
    def ram_usage(self) -> float:
        """Gets the ram_usage of this VmItem.

        ram usage in percent  # noqa: E501

        :return: The ram_usage of this VmItem.
        :rtype: float
        """
        return self._ram_usage

    @ram_usage.setter
    def ram_usage(self, ram_usage: float):
        """Sets the ram_usage of this VmItem.

        ram usage in percent  # noqa: E501

        :param ram_usage: The ram_usage of this VmItem.
        :type ram_usage: float
        """

        self._ram_usage = ram_usage

    @property
    def uptime(self) -> float:
        """Gets the uptime of this VmItem.

        VM's uptime in sec  # noqa: E501

        :return: The uptime of this VmItem.
        :rtype: float
        """
        return self._uptime

    @uptime.setter
    def uptime(self, uptime: float):
        """Sets the uptime of this VmItem.

        VM's uptime in sec  # noqa: E501

        :param uptime: The uptime of this VmItem.
        :type uptime: float
        """

        self._uptime = uptime

    @property
    def last_backup_date(self) -> float:
        """Gets the uptime of this VmItem.

        VM's uptime in sec  # noqa: E501

        :return: The uptime of this VmItem.
        :rtype: float
        """
        return self._last_backup_date

    @last_backup_date.setter
    def last_backup_date(self, last_backup_date: float):
        """Sets the uptime of this VmItem.

        VM's uptime in sec  # noqa: E501

        :param uptime: The uptime of this VmItem.
        :type uptime: float
        """

        self._last_backup_date = last_backup_date

    @property
    def created_on(self) -> str:
        """Gets the created_on of this VmItem.

        creation date of the VM  # noqa: E501

        :return: The created_on of this VmItem.
        :rtype: str
        """
        return self._created_on

    @created_on.setter
    def created_on(self, created_on: str):
        """Sets the created_on of this VmItem.

        creation date of the VM  # noqa: E501

        :param created_on: The created_on of this VmItem.
        :type created_on: str
        """

        self._created_on = created_on