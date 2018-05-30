from copy import deepcopy
import re


class KeyValueType(object):

    def __init__(self, pattern, key_type=str, value_type=str, prefix_pattern=""):
        """ given a string the class will generate a dictionary with declared key and value types

        Object will perform a regex pattern match and expect a 'key' and 'value' named
        capturing group it will automatically return a {key: value} dict.

        Args:
            pattern (str): regex pattern
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
                return {match.groupdict()["key"]: match.groupdict()["value"]}

        return {string: ""}


class BaseAssumptions(object):
    """ A simple rule: action store that allows inhering another store

    """

    def __init__(self, assumptions={}, parent_assumptions={}, inherits=True):
        super(BaseAssumptions, self).__init__()

        self._assumptions = assumptions
        self._parent_assumptions = parent_assumptions
        self._inherits = inherits

    def call_action(self, value):
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
        _assumptions = self._parent_assumptions
        assumptions = deepcopy(self._assumptions)
        if self._inherits:
            assumptions.update(_assumptions)
        return assumptions


class TypeAssumptions(BaseAssumptions):

    assumptions = {"^(\d+)$": int,
                   "^(\d+\.\d+)$": float
                   }

    def __init__(self,  assumptions={}, parent_assumptions=assumptions, inherit=True):
        super(TypeAssumptions, self).__init__(assumptions, parent_assumptions, inherit)


class TypeAssumptionError(ValueError):
    pass
