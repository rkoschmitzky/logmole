from copy import deepcopy
import datetime
import logging
import re

from .utilities import chunks

LOG = logging.getLogger("logmole.types")


class TimeType(object):
    """ given a string the class will generate a datetime.time object

    Object will automatically detect a time signature under specific conditions
    - `:`separated
    - given at least hour:minute:second
    - hours < 24
    - minutes < 60
    - seconds < 60
    - microseconds < 999999

    microsecond can be detected as well, but is considered as optional
    """
    def __call__(self, string):
        # we always expect always h:m:s information h:m:s:ms is optional
        pattern = r"^(?P<h>\d{1,2})\:(?P<m>\d{1,2})\:(?P<s>\d{1,2})(\:(?P<ms>\d{1,6}))?$"

        match = re.match(pattern, string)
        if match:

            # convert non existing microseconds
            group_dict = match.groupdict()
            if group_dict["ms"] is None:
                group_dict["ms"] = 0

            time = [int(group_dict["h"]), int(group_dict["m"]), int(group_dict["s"]), int(group_dict["ms"])]

            if time[0] < 24 and time[1] <= 60 and time[2] < 60 and time[3] <= 999999:
                return datetime.time(*time)
            else:
                try:
                    raise TypeAssumptionError("No valid time signature.")
                except TypeAssumptionError:
                    LOG.error("Unable to convert '{}' to time object.", exc_info=True)

        return string


class TwoDimensionalNumberArray(object):
    """ given a string the class will generate a two dimensional array/list

    Object will perform a regex pattern match and expect a 'number' named capturing
    group to identify what to consider as number inside the arrays' items.

    Args:
        pattern (str): regex pattern
    Keyword Args:
        item_array_size (int): length each individual item will have

    Notes:
        Expects that all items will use the same amount of numbers.

    """
    def __init__(self, pattern, item_array_size=1):
        self._pattern = pattern
        self._item_array_size = item_array_size

    def __call__(self, string):
        match = [_ for _ in re.finditer(self._pattern, string)]

        if match:
            return [chunk for chunk in chunks(
                        [float(_.groupdict()["number"]) for _ in match],
                        self._item_array_size
                        )
                    ]

        return string


class KeyValueType(object):

    def __init__(self, pattern, key_type=str, value_type=str, prefix_pattern=""):
        """ given a string the class will generate a dictionary with declared key and value types

        Object will perform a regex pattern match and expect a 'key' and 'value' named
        capturing group it will automatically return a {key: value} dict.

        Args:
            pattern (str): regex pattern
        Keyword Args:
            key_type (cls): type the potential found key will be
            value_type (cls): type the potential found value will have
            prefix_pattern (str): regex pattern, if set it expects a 'key' named capturing group
                                  Allows you to extract a specific part of the string and prefix the found 'key' matches
                                  This is only supported if key_type is str

        Examples:
            >>> input_string = "transmission      samples  2 / depth  2"
            >>> convert =  KeyValueType(r"(?P<key>\w+)\s+(?P<value>\d+)", value_type=int, prefix_pattern=r"(?P<key>^\w+\s)")
            >>> print convert(input_string)
            {"transmission depth": 8,
             "transmission samples": 2}

        """
        self._key_type = key_type
        self._value_type = value_type
        self._pattern = pattern
        self._prefix_pattern = prefix_pattern

    def __call__(self, string):
        """ converts the original value

        Args:
            string (str): the original value that will be converted

        Returns:
            dict: included key value pair

        """

        # validate proper usage
        if not ("?P<key>" or "?P<value>") in self._pattern:
            raise TypeAssumptionError("{} needs ".format(self.__class__.__name__) +
                                      "a 'key' and 'value' named capturing group."
                                      )
        if self._prefix_pattern and "?P<key>" not in self._prefix_pattern:
            raise TypeAssumptionError("{} prefix pattern needs ".format(self.__class__.__name__) +
                                      "a 'key' named capturing group."
                                      )

        # lets find the prefix
        if self._prefix_pattern:
            match = re.search(self._prefix_pattern, string)
            if not match:
                raise TypeAssumptionError("No prefix match using '{0}' found in '{1}'.".format(self._prefix_pattern, string))
            key_prefix = match.groupdict().get("key", None)

        if self._prefix_pattern:
            # lets apply the prefix to all 'key' founds
            match = [_ for _ in re.finditer(self._pattern, string)]
            if match:
                match = [_.groupdict() for _ in match]
                if self._prefix_pattern:
                    assert self._key_type is str, "Prefix support only for string instances"
                    return {key_prefix + _["key"]: self._value_type(_["value"]) for _ in match}

                return {string: ""}
        else:
            # lets assume we have unique keys and values
            match = re.search(self._pattern, string)
            if match:
                return {self._key_type(match.groupdict()["key"]): self._value_type(match.groupdict()["value"])}

        return {string: ""}


class NoneType(object):
    """ Lets make None a callable which always converts to None """

    def __call__(self, string):
        return None


class BaseAssumptions(object):
    """ A simple rule: action store that allows inhering another stores

    """

    def __init__(self, assumptions={}, parent_assumptions={}, inherits=True):
        super(BaseAssumptions, self).__init__()

        self._assumptions = assumptions
        self._parent_assumptions = parent_assumptions
        self._inherits = inherits

    def call_action(self, value):
        """ Calls expected action for when there is an assumed pattern match """
        if not isinstance(value, str):
            raise TypeAssumptionError("Value has to be of type 'str'.")
        results = []
        for pattern, action in self.get().iteritems():
            if re.match(pattern, value):
                if results:
                    raise TypeAssumptionError("Multiple assumptions matching on value {}".format(value))
                results.append(action(value))
        if results:
            return results[0]
        else:
            return value

    def get(self):
        """ If the Assumption will inherit parent assumptions add them and get the updated result """
        _assumptions = self._parent_assumptions
        assumptions = deepcopy(self._assumptions)
        if self._inherits:
            assumptions.update(_assumptions)
        return assumptions


class TypeAssumptions(BaseAssumptions):

    # handle all obvious assumptions we can make
    assumptions = {
        "^(\-?\d+)$": int,
        "^(\-?\d+\.\d+)$": float,
        "^((N|n)one)$|^NONE$|^((N|n)ull)$|^NULL$|^((N|n)il)$|^NIL$": NoneType()
    }

    def __init__(self,  assumptions={}, parent_assumptions=assumptions, inherit=True):
        super(TypeAssumptions, self).__init__(assumptions, parent_assumptions, inherit)


class TypeAssumptionError(ValueError):
    pass
