import re

class ContainerMeta(type):

    patterns = {}

    def __new__(cls, name, bases, attrs):
        if attrs.get("pattern"):
            cls.patterns[name] = attrs["pattern"]
            bases[0].patterns = cls.patterns
        return super(ContainerMeta, cls).__new__(cls, name, bases, attrs)


class LogContainer(object):

    __metaclass__ = ContainerMeta

    sub_containers = []
    representative = ""
    pattern = None
    regex = ""

    def __init__(self):
        self._named_group_filter = re.compile("\?P<(\w*)>")
        self._add_chain_patterns(self.sub_containers)
        self._add_representative(self.sub_containers, self)

    def _add_chain_patterns(self, containers):
        for container in containers:
            container_pattern = self.patterns[container.__name__]
            for named_group in self._named_group_filter.findall(container_pattern):
                container_pattern = container_pattern.replace(named_group, "{0}_{1}".format(container.__name__,
                                                                                            named_group))
            self.regex += container_pattern + "|"
            self._add_chain_patterns(container.sub_containers)

    def _add_representative(self, containers, parent):
        for container in containers:
            if container.representative:
                setattr(parent, container.representative, type("Container", (object, ), {}))

                self._add_representative(container.sub_containers, getattr(parent, container.representative))