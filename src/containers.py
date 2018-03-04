import re


class ContainerMeta(type):

    patterns = {}

    def __new__(mcs, name, bases, attrs):
        if attrs.get("pattern"):
            mcs.patterns[name] = attrs["pattern"]
            bases[0].patterns = mcs.patterns
        return super(ContainerMeta, mcs).__new__(mcs, name, bases, attrs)


class LogContainer(object):

    __metaclass__ = ContainerMeta

    sub_containers = []
    representative = ""
    pattern = None
    _regex = ""

    def __init__(self, file):
        self._file = file
        self._groups_map = {}
        self._named_group_filter = re.compile("\?P<(\w*)>")
        self._generate_chain(self.sub_containers, self)
        self._add_group_content()

    @property
    def regex(self):
        return self._regex[:-1]

    @staticmethod
    def _group_prefix(cls):
        return cls.__name__ + "_"

    def _group_name(self, cls, named_group):
        return self._group_prefix(cls) + named_group

    def _add_pattern(self, cls):
        container_pattern = self.patterns[cls.__name__]
        named_groups = []
        for named_group in self._named_group_filter.findall(container_pattern):
            container_pattern = container_pattern.replace(named_group, self._group_name(cls, named_group))
            named_groups.append(named_group)
        self._regex += container_pattern + "|"
        return named_groups

    def _create_members(self, cls, representative):
        container_named_groups = self._add_pattern(cls)
        for named_group in container_named_groups:
            setattr(representative, named_group, None)
            self._groups_map[self._group_name(cls, named_group)] = {"obj": representative,
                                                                    "attr": named_group
                                                                    }

    def _generate_chain(self, containers, parent):
        if parent == self:
            print "test"
            self._create_members(parent.__class__, self)

        for container in containers:
            # create members
            if container.representative:
                setattr(parent, container.representative, type("LogContainer",
                                                               (LogContainer, ),
                                                               {"representative": container.representative,
                                                                "pattern": container.pattern}
                                                               )
                        )
                representative = getattr(parent, container.representative)
            else:
                representative = parent

            self._create_members(container, representative)

            # continue generating chain
            self._generate_chain(container.sub_containers, representative)

    def _add_group_content(self):
        with open(self._file) as f:
            for match in regex_finditer_filter(f, self.regex):
                for _ in match:
                    for key, value in _.groupdict().iteritems():
                        if value:
                            print "found value for ", key
                            # todo: check if the attribute we want to set exists
                            setattr(self._groups_map[key]["obj"], self._groups_map[key]["attr"], value)


def regex_finditer_filter(lines, pattern):
    _compiled = re.compile(pattern)
    for line in lines:
        yield _compiled.finditer(line)
