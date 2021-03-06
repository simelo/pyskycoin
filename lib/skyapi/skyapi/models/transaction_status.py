# coding: utf-8

"""
    Skycoin REST API.

    Skycoin is a next-generation cryptocurrency.  # noqa: E501

    OpenAPI spec version: 0.26.0
    Contact: contact@skycoin.net
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class TransactionStatus(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'block_seq': 'int',
        'confirmed': 'bool',
        'height': 'int',
        'unconfirmed': 'bool'
    }

    attribute_map = {
        'block_seq': 'block_seq',
        'confirmed': 'confirmed',
        'height': 'height',
        'unconfirmed': 'unconfirmed'
    }

    def __init__(self, block_seq=None, confirmed=None, height=None, unconfirmed=None):  # noqa: E501
        """TransactionStatus - a model defined in OpenAPI"""  # noqa: E501

        self._block_seq = None
        self._confirmed = None
        self._height = None
        self._unconfirmed = None
        self.discriminator = None

        if block_seq is not None:
            self.block_seq = block_seq
        if confirmed is not None:
            self.confirmed = confirmed
        if height is not None:
            self.height = height
        if unconfirmed is not None:
            self.unconfirmed = unconfirmed

    @property
    def block_seq(self):
        """Gets the block_seq of this TransactionStatus.  # noqa: E501

        If confirmed, the sequence of the block in which the transaction was executed  # noqa: E501

        :return: The block_seq of this TransactionStatus.  # noqa: E501
        :rtype: int
        """
        return self._block_seq

    @block_seq.setter
    def block_seq(self, block_seq):
        """Sets the block_seq of this TransactionStatus.

        If confirmed, the sequence of the block in which the transaction was executed  # noqa: E501

        :param block_seq: The block_seq of this TransactionStatus.  # noqa: E501
        :type: int
        """

        self._block_seq = block_seq

    @property
    def confirmed(self):
        """Gets the confirmed of this TransactionStatus.  # noqa: E501


        :return: The confirmed of this TransactionStatus.  # noqa: E501
        :rtype: bool
        """
        return self._confirmed

    @confirmed.setter
    def confirmed(self, confirmed):
        """Sets the confirmed of this TransactionStatus.


        :param confirmed: The confirmed of this TransactionStatus.  # noqa: E501
        :type: bool
        """

        self._confirmed = confirmed

    @property
    def height(self):
        """Gets the height of this TransactionStatus.  # noqa: E501

        If confirmed, how many blocks deep in the chain it is. Will be at least 1 if confirmed  # noqa: E501

        :return: The height of this TransactionStatus.  # noqa: E501
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this TransactionStatus.

        If confirmed, how many blocks deep in the chain it is. Will be at least 1 if confirmed  # noqa: E501

        :param height: The height of this TransactionStatus.  # noqa: E501
        :type: int
        """

        self._height = height

    @property
    def unconfirmed(self):
        """Gets the unconfirmed of this TransactionStatus.  # noqa: E501


        :return: The unconfirmed of this TransactionStatus.  # noqa: E501
        :rtype: bool
        """
        return self._unconfirmed

    @unconfirmed.setter
    def unconfirmed(self, unconfirmed):
        """Sets the unconfirmed of this TransactionStatus.


        :param unconfirmed: The unconfirmed of this TransactionStatus.  # noqa: E501
        :type: bool
        """

        self._unconfirmed = unconfirmed

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, TransactionStatus):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
