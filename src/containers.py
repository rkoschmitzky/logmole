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

    group_prefixes = []
    sub_containers = []
    representative = ""
    pattern = None
    _regex = ""

    def __init__(self):
        self._named_group_filter = re.compile("\?P<(\w*)>")
        self._generate_chain(self.sub_containers, self)

    @staticmethod
    def _group_prefix(container):
        return container.__name__ + "_"

    def _group_name(self, container, named_group):
        return self._group_prefix(container) + named_group

    def _add_pattern(self, container):
        container_pattern = self.patterns[container.__name__]
        named_groups = []
        for named_group in self._named_group_filter.findall(container_pattern):
            container_pattern = container_pattern.replace(named_group, self._group_name(container, named_group))
            named_groups.append(named_group)
        self._regex += container_pattern + "|"
        return named_groups

    def _generate_chain(self, containers, parent):
        """ generates the regex pattern chain and container members

        Args:
            containers:
            parent:

        Returns:

        """
        for container in containers:
            # create members
            if container.representative:
                setattr(parent, container.representative, type("Content",
                                                               (Content, ),
                                                               {"representative": container.representative,
                                                                "group_prefixes": [self._group_prefix(container)]}
                                                               )
                        )
                representative = getattr(parent, container.representative)
            else:
                representative = parent
                # store the named group prefixes we are using
                parent.group_prefixes.append(self._group_prefix(container))

            # adding additional members for all named groups we detect
            container_named_groups = self._add_pattern(container)
            for named_group in container_named_groups:
                setattr(representative, named_group, "")

            # continue generating chain
            self._generate_chain(container.sub_containers, representative)