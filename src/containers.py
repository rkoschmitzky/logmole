import logging
import re
import sys

LOG = logging.getLogger("logmole.container")
logging.basicConfig(stream=sys.__stdout__, level=logging.INFO)


class LogContainer(object):
    sub_containers = []
    representative = ""
    pattern = None
    _regex = ""

    def __init__(self, file):
        self._groups_map = {}
        self._named_group_filter = re.compile("\?P<(\w*)>")
        self._generate_chain(self.sub_containers, self)
        self._parse_file(file)

    @property
    def regex(self):
        """ global regex pattern

        Returns:
            str: regex pattern

        """
        return self._regex[:-1]

    @staticmethod
    def _group_prefix(cls):
        """ intended named capturing group prefix

        Args:
            cls (LogContainer): container

        Returns:
            str: named capturing prefix

        """
        return cls.__name__ + "_"

    def _group_name(self, cls, named_group):
        """

        Args:
            cls (LogContainer): container
            named_group (str): name of the capturing group

        Returns:

        """
        return self._group_prefix(cls) + named_group

    def _append_pattern(self, cls):
        """ appends the container pattern to the global regex using the "|" alternator

        Args:
            cls (LogContainer): container

        Returns:
            list: found named capturing groups

        """
        container_pattern = cls.pattern

        named_groups = self._named_group_filter.findall(container_pattern)
        if not named_groups:
            LOG.warning("Container '{0}' pattern '{1}' ".format(cls.__name__, cls.pattern) + \
                        "doesn't include a named capturing group. " + \
                        "No matches will be added.")

        for named_group in named_groups:
            container_pattern = container_pattern.replace(named_group, self._group_name(cls, named_group))
        self._regex += container_pattern + "|"
        return named_groups

    def _create_members(self, cls, representative):
        """ checks the container pattern and adds found members to its representative

        Args:
            cls (LogContainer): container
            representative (cls): representative container

        Returns:

        """
        container_named_groups = self._append_pattern(cls)
        for named_group in container_named_groups:
            assert not hasattr(representative, named_group), \
            "Conflicting group name '{0}' on '{1}'.".format(named_group, representative.__class__.__name__)

            setattr(representative, named_group, None)
            self._groups_map[self._group_name(cls, named_group)] = {"obj": representative,
                                                                    "attr": named_group
                                                                    }

    def _generate_chain(self, containers, parent):
        """ recursively chains container patterns and members

        Args:
            containers (list): container classes
            parent (:obj:`LogContainer`): parent container, which can be a sub-container class or the main instance

        Returns:

        """
        # our main container will be the instance itself
        if parent == self:
            self._create_members(parent.__class__, self)

        for container in containers:
            # create members
            if container.representative:
                setattr(parent, container.representative, type("LogContainer",
                                                               (LogContainer,),
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

    def _parse_file(self, filepath):
        """ parses the file and add the results to their corresponding member

        Args:
            filepath (str): path to file

        Returns:

        """
        with open(filepath) as f:
            for match in regex_finditer_filter(f, self.regex):
                for _ in match:
                    for key, value in _.groupdict().iteritems():
                        # check if the match group key has a real value
                        if value:
                            # check if we added a value before
                            existing_match = getattr(self._groups_map[key]["obj"], self._groups_map[key]["attr"])
                            # in case there is something convert it and add the new match to it
                            if existing_match and self._groups_map[key]["obj"]:
                                if isinstance(existing_match, list):
                                    existing_match.append(value)
                                    existing_match = sorted(set(existing_match))
                                else:
                                    existing_match = [existing_match]
                            else:
                                # otherwise simple add the string value
                                existing_match = value

                            setattr(self._groups_map[key]["obj"], self._groups_map[key]["attr"], existing_match)


def regex_finditer_filter(lines, pattern):
    """ regex filter

    Args:
        lines (:obj:`list` of `str`):
        pattern (str): regex pattern

    Yields:
        iterator: match groups


    """
    _compiled = re.compile(pattern)
    for line in lines:
        yield _compiled.finditer(line)