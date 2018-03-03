import re

class ContainerMeta(type):

    patterns = {}

    def __new__(cls, name, bases, attrs):
        if attrs.get("pattern"):
            cls.patterns[name] = attrs["pattern"]
            bases[0].patterns = cls.patterns
        return super(ContainerMeta, cls).__new__(cls, name, bases, attrs)


class Content(object):
    pass


class LogContainer(object):

    __metaclass__ = ContainerMeta

    sub_containers = []
    representative = ""
    pattern = None
    regex = ""

    def __init__(self):
        self._named_group_filter = re.compile("\?P<(\w*)>")
        self._generate_chain(self.sub_containers, self)
        #self._add_representative(self.sub_containers, self)


    @staticmethod
    def _group_prefix(container):
        return container.__name__ + "_"

    def _group_name(self, container, named_group):
        return self._group_prefix(container) + named_group

    def _generate_chain(self, containers, parent):
        """ generates the regex pattern chain and container members

        Args:
            containers:
            parent:

        Returns:

        """
        for container in containers:
            container_pattern = self.patterns[container.__name__]
            for named_group in self._named_group_filter.findall(container_pattern):
                container_pattern = container_pattern.replace(named_group, self._group_name(container, named_group))
            self.regex += container_pattern + "|"

            if container.representative:
                setattr(parent, container.representative, type("Content",
                                                               (Content, ),
                                                               {"representative": container.representative,
                                                                "group_prefix": self._group_prefix(container)}
                                                               )
                        )

            self._generate_chain(container.sub_containers, getattr(parent, container.representative))