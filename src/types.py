import re


class KeyValueType(object):

    def __init__(self, pattern, key_type, value_type):
        self._key_type = key_type
        self._value_type = value_type
        self._pattern = pattern

    def __call__(self, string):
        match = re.search(self._pattern, string)
        if match:
            assert "key" and "value" in match.groupdict(), "{} needs ".format(self.__class__.__name__) + \
                                                           "a 'key' and 'value' named capturing group."
            return {match.groupdict()["key"]:
                    match.groupdict()["value"]
                    }
        return {string: ""}


class TypeAssumptions(dict):

    def __init__(self):
        self["^(\d+)$"] = int
        self["^(\d+\.\d+)$"] = float

    def __call__(self, value):
        # todo catch case when we would have multiple assumptions matching
        for pattern, _type in self.iteritems():
            if re.match(pattern, value):
                return _type(value)
        return value
