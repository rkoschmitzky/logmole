from copy import deepcopy
import re


class KeyValueType(object):

    def __init__(self, pattern, key_type, value_type):
        """ given a string the class will generate a dictionary with declared key and value types

        Object will perform a regex pattern match and expect a 'key' and 'value' named
        capturing group it will automatically return a {key: value} dict.

        Args:
            pattern (str): regex pattern
            key_type (cls): type the potential found key will be
            value_type (cls): type the potential found value will have
        """
        self._key_type = key_type
        self._value_type = value_type
        self._pattern = pattern

    def __call__(self, string):
        """ converts the original value

        Args:
            string (str): the original value that will be converted

        Returns:
            dict: included key value pair

        """
        match = re.search(self._pattern, string)
        if match:
            if not ("key" or "value") in match.groupdict():
                raise TypeAssumptionError("{} needs ".format(self.__class__.__name__) +
                                          "a 'key' and 'value' named capturing group."
                                          )
            return {self._key_type(match.groupdict()["key"]):
                        self._value_type(match.groupdict()["value"])
                    }
        return {string: ""}


class BaseAssumptions(object):
    """ An simple rule: action store that allows inhering another store

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
