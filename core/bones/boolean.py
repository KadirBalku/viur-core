"""
    The BooleanBone class represents a boolean data type, which can have two possible values: True or False. It is a subclass of the BaseBone class and is used in the context of the ViUR web application framework.
"""
from viur.core.bones.base import BaseBone, ReadFromClientError, ReadFromClientErrorSeverity
from viur.core import db, conf
from typing import Dict, Optional, Any


class BooleanBone(BaseBone):
    """
    Represents a boolean data type, which can have two possible values: `True` or `False`.

    :param defaultValue: The default value of the `BooleanBone` instance. Defaults to `False`.
    :type defaultValue: bool
    :raises ValueError: If the `defaultValue` is not a boolean value (`True` or `False`).
    """
    type = "bool"

    def __init__(
        self,
        *,
        defaultValue: bool = False,
        **kwargs
    ):
        if defaultValue not in (True, False):
            raise ValueError("Only 'True' or 'False' can be provided as BooleanBone defaultValue")

        super().__init__(defaultValue=defaultValue, **kwargs)

    def singleValueFromClient(self, value, skel: 'viur.core.skeleton.SkeletonInstance', name: str, origData):
        """
        Converts a value received from a client into a boolean value.

        :param value: The value received from the client.
        :param skel: The `SkeletonInstance` object representing the data of the current entity.
        :param name: The name of the `BooleanBone` instance.
        :param origData: The original data received from the client.

        :return: A tuple containing the boolean value and `None`.
        :rtype: Tuple[bool, None]
        """
        return str(value).strip().lower() in conf["viur.bone.boolean.str2true"], None

    def getEmptyValue(self):
        """
        Returns the empty value of the `BooleanBone` class, which is `False`.

        :return: The empty value of the `BooleanBone` class (`False`).
        :rtype: bool
        """
        return False

    def isEmpty(self, rawValue: Any):
        """
        Checks if the given boolean value is empty.

        :param rawValue: The boolean value to be checked.
        :return: `True` if the boolean value is empty (i.e., equal to the empty value of the `BooleanBone` class), `False` otherwise.
        :rtype: bool
        """
        if rawValue is self.getEmptyValue():
            return True
        return not bool(rawValue)

    def refresh(self, skel: 'viur.core.skeleton.SkeletonInstance', boneName: str) -> None:
        """
            Inverse of serialize. Evaluates whats
            read from the datastore and populates
            this bone accordingly.

            :param name: The property-name this bone has in its Skeleton (not the description!)
        """
        if not isinstance(skel[boneName], bool):
            skel[boneName] = str(skel[boneName]).strip().lower() in conf["viur.bone.boolean.str2true"]

    def buildDBFilter(
        self,
        name: str,
        skel: 'viur.core.skeleton.SkeletonInstance',
        dbFilter: db.Query,
        rawFilter: Dict,
        prefix: Optional[str] = None
    ) -> db.Query:
        """
        Builds a database filter based on the boolean value.

        :param name: The name of the `BooleanBone` instance.
        :param skel: The `SkeletonInstance` object representing the data of the current entity.
        :param dbFilter: The `Query` object representing the current database filter.
        :param rawFilter: The dictionary representing the raw filter data received from the client.
        :param prefix: A prefix to be added to the property name in the database filter.
        :return: The updated `Query` object representing the updated database filter.
        :rtype: google.cloud.ndb.query.Query
        """
        if name in rawFilter:
            val = str(rawFilter[name]).strip().lower() in conf["viur.bone.boolean.str2true"]
            return super().buildDBFilter(name, skel, dbFilter, {name: val}, prefix=prefix)

        return dbFilter
