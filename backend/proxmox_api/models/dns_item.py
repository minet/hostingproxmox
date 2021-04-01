# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from proxmox_api.models.base_model_ import Model
from proxmox_api import util


class DnsItem(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, entry: str=None, ip: str=None):  # noqa: E501
        """DnsItem - a model defined in Swagger

        :param entry: The entry of this DnsItem.  # noqa: E501
        :type entry: str
        :param ip: The ip of this DnsItem.  # noqa: E501
        :type ip: str
        """
        self.swagger_types = {
            'entry': str,
            'ip': str
        }

        self.attribute_map = {
            'entry': 'entry',
            'ip': 'ip'
        }
        self._entry = entry
        self._ip = ip

    @classmethod
    def from_dict(cls, dikt) -> 'DnsItem':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The DnsItem of this DnsItem.  # noqa: E501
        :rtype: DnsItem
        """
        return util.deserialize_model(dikt, cls)

    @property
    def entry(self) -> str:
        """Gets the entry of this DnsItem.

        dns entry  # noqa: E501

        :return: The entry of this DnsItem.
        :rtype: str
        """
        return self._entry

    @entry.setter
    def entry(self, entry: str):
        """Sets the entry of this DnsItem.

        dns entry  # noqa: E501

        :param entry: The entry of this DnsItem.
        :type entry: str
        """
        if entry is None:
            raise ValueError("Invalid value for `entry`, must not be `None`")  # noqa: E501

        self._entry = entry

    @property
    def ip(self) -> str:
        """Gets the ip of this DnsItem.

        entry to this ip  # noqa: E501

        :return: The ip of this DnsItem.
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip: str):
        """Sets the ip of this DnsItem.

        entry to this ip  # noqa: E501

        :param ip: The ip of this DnsItem.
        :type ip: str
        """
        if ip is None:
            raise ValueError("Invalid value for `ip`, must not be `None`")  # noqa: E501

        self._ip = ip
