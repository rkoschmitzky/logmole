from collections import OrderedDict
import json
import os
import tempfile
import uuid
from unittest import TestCase

from ..src.logmole import LogContainer

from .fixtures import containers


def init_mock(self, *args, **kwargs):
    self._groups_map = {}


class TestContainer(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._log = os.path.join(os.path.dirname(containers.__file__), "log")
        with open(cls._log, "r") as f:
            cls._logstream = f.read()
        cls._patched_container = type("PatchContainer", (containers.ParentsContainer,), {"__init__": init_mock})
        cls._expected_dict = OrderedDict(
            [
                (
                    'children', {
                        'child1': {
                            'name': 'Dave'
                        },
                        'child2': {
                            'name': 'Lea'
                        }
                    }
                ),
                (
                    'parents', {
                        'father': 'Peter', 'mother': 'Jane'
                    }
                )
            ]
        )

    def test_group_detection(self):
        with self.assertRaises(ValueError) as e:
            containers.MissingGroupContainer(self._log)
            self.assertIn("doesn't include a capturing group", e.exception.message)

    def test_infer_type_conflicts(self):
        with self.assertRaises(AssertionError) as e:
            containers.InterTypeConflictsContainer(self._log)
            self.assertIn("infer_type state conflicts", e.exception.message)

    def test_regex_chain_and_mapping(self):
        x = self._patched_container(self._log)
        x._generate_chain(x.sub_containers, x, init=True)

        expected_containers = [
            "MotherContainer_mother",
            "FatherContainer_father",
            "Child1Container_name",
            "Child2Container_name"
        ]
        patterns = [
            r"mother:\s(?P<{0}>.*)",
            r"father:\s(?P<{1}>.*)",
            r"child1:\s(?P<{2}>.*)",
            r"child2:\s(?P<{3}>.*)"
        ]

        # check pattern
        self.assertEqual(r"|".join(patterns).format(*expected_containers), x.regex)

        # check group maps content
        for container in expected_containers:
            self.assertIn(container, x._groups_map)

        # checking the groups mapping
        self.assertEqual(x._groups_map[expected_containers[0]]["member_name"], "parents.mother")
        self.assertEqual(x._groups_map[expected_containers[0]]["attr"], "mother")
        self.assertEqual(x._groups_map[expected_containers[1]]["member_name"], "parents.father")
        self.assertEqual(x._groups_map[expected_containers[1]]["attr"], "father")
        self.assertEqual(x._groups_map[expected_containers[2]]["member_name"], "children.child1.name")
        self.assertEqual(x._groups_map[expected_containers[2]]["attr"], "name")
        self.assertEqual(x._groups_map[expected_containers[3]]["member_name"], "children.child2.name")
        self.assertEqual(x._groups_map[expected_containers[3]]["attr"], "name")

    def test_members(self):

        for file_or_stream in [self._log, self._logstream]:
            x = containers.ParentsContainer(file_or_stream)

            self.assertTrue(hasattr(x, "parents"))
            self.assertTrue(hasattr(x.parents, "father"))
            self.assertTrue(hasattr(x.parents, "mother"))
            self.assertTrue(hasattr(x, "children"))
            self.assertTrue(hasattr(x.children, "child1"))
            self.assertTrue(hasattr(x.children.child1, "name"))
            self.assertTrue(hasattr(x.children, "child2"))
            self.assertTrue(hasattr(x.children.child2, "name"))

            self.assertTrue(issubclass(x.parents, LogContainer))
            self.assertTrue(issubclass(x.children, LogContainer))
            self.assertTrue(issubclass(x.children.child1, LogContainer))
            self.assertTrue(issubclass(x.children.child2, LogContainer))

    def test_tree(self):
        for file_or_stream in [self._log, self._logstream]:
            self.assertDictEqual(
                containers.ParentsContainer(file_or_stream)._tree,
                self._expected_dict
            )

    def test_get_value(self):

        for file_or_stream in [self._log, self._logstream]:
            x = containers.ParentsContainer(file_or_stream)

            self.assertIsNone(x.get_value("mother"))
            self.assertEqual(x.get_value("parents", default=6), 6)
            self.assertEqual(x.get_value("parents.father"), "Peter")
            self.assertEqual(x.get_value("parents.mother"), "Jane")
            self.assertEqual(x.get_value("children.child1.name"), "Dave")
            self.assertEqual(x.get_value("children.child2.name"), "Lea")


    def test_dump(self):

        path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + ".json")
        containers.ParentsContainer(self._log).dump(path)

        with self.assertRaises(IOError) as e:
            containers.ParentsContainer(self._log).dump("/++/")

        # check file existence
        self.assertTrue(os.path.exists(path))

        # check file content
        f = open(path, "r")
        self.assertDictEqual(json.loads(f.read()), self._expected_dict)

    def test_multi_match(self):

        x = containers.MultiMatchContainer(self._log)

        self.assertIsInstance(x.family, list)
        self.assertListEqual(sorted(x.family), ["Dave", "Jane", "Lea", "Peter"])

        x = containers.MultiMatchToDictContainer(self._log)
        self.assertDictEqual(x.family, {'child1': 'Dave',
                                        'child2': 'Lea',
                                        'father': 'Peter',
                                        'mother': 'Jane'}
                             )
