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
            return {match.groupdict()["key"]:
                    match.groupdict()["value"]
                    }
        return {string: ""}


class BaseAssumptions(dict):

    assumptions = {}

    def __init__(self, assumptions={}, ignore_base_assumptions=False):
        super(BaseAssumptions, self).__init__()

        # fill assumptions
        if not ignore_base_assumptions:
            self.assumptions.update(assumptions)
        for request, action in self.assumptions.iteritems():
            self[request] = action

    def __call__(self, value):
        results = []
        for pattern, action in self.iteritems():
            if re.match(pattern, value):
                if results:
                    raise TypeAssumptionError("Multiple assumptions matching on value {}".format(value))
                results.append(action(value))
        if results:
            return results[0]
        else:
            return value


class TypeAssumptions(BaseAssumptions):

    assumptions = {"^(\d+)$": int,
                   "^(\d+\.\d+)$": float
                   }

    def __init__(self,  assumptions={}, ignore_base_assumptions=False):
        super(TypeAssumptions, self).__init__(assumptions, ignore_base_assumptions)


class TypeAssumptionError(ValueError):
    pass
