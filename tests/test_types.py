from datetime import time
from unittest import (
    mock,
    TestCase
)

from ..src.logmole import (
    KeyValueType,
    TimeType,
    TwoDimensionalNumberArrayType,
    GenericAssumptions
)


class TestGenericAssumptions(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._assumptions = GenericAssumptions()

    def test_call_action(self):
        self.assertEqual(-2, self._assumptions.call_action("-2"))
        self.assertEqual(5, self._assumptions.call_action("5"))
        self.assertEqual(5.0, self._assumptions.call_action("5.0"))
        self.assertEqual(-1.0, self._assumptions.call_action("-1.0"))
        self.assertEqual(None, self._assumptions.call_action("None"))
        self.assertEqual(None, self._assumptions.call_action("nil"))
        self.assertEqual(None, self._assumptions.call_action("Null"))
        self.assertEqual(None, self._assumptions.call_action("null"))
        self.assertEqual(None, self._assumptions.call_action("Nil"))
        self.assertEqual(None, self._assumptions.call_action("none"))
        self.assertEqual(None, self._assumptions.call_action("NONE"))
        self.assertEqual(None, self._assumptions.call_action("NIL"))
        self.assertEqual(None, self._assumptions.call_action("NULL"))
        self.assertEqual("NUll", self._assumptions.call_action("NUll"))


class TestKeyValueType(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.key_value_type = None

    def test_call_simple(self):
        with mock.patch.object(self, "key_value_type",
                               KeyValueType("(?P<key>[a-z])+\=(?P<value>\d+)$",
                                            value_type=float)
                               ):
            self.assertDictEqual({"a": 1.0}, self.key_value_type("a=1"))
            # default behaviour when there is no match
            self.assertEqual({"bc=5.0.0": ""}, self.key_value_type("bc=5.0.0"))

    def test_call_invalid_pattern(self):
        with mock.patch.object(self, "key_value_type",
                               KeyValueType("(P?<test>.*)")):
            with self.assertRaises(ValueError) as e:
                self.key_value_type("a")
                self.assertIn("needs a 'key' and 'value' named capturing group")

    def test_call_with_prefix_pattern(self):
        with mock.patch.object(self, "key_value_type",
                               KeyValueType("(?P<value>\d+)\s(?P<key>[a-z]+)",
                                            value_type=int,
                                            prefix_pattern="(?P<key>[a-z]+):")):
            self.assertDictEqual({'testfoo': 1, 'testbar': 2},
                                 self.key_value_type("test: 1 foo, 2 bar"))


class TestTimeType(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.time_type = None

    def test_call(self):
        with mock.patch.object(self, "time_type",
                               TimeType()):
            self.assertEqual(time(5, 6, 3), self.time_type("5:6:3"))
            self.assertEqual(time(5, 6, 3), self.time_type("05:6:3"))
            self.assertEqual(time(5, 6, 3, 0), self.time_type("5:6:3:00000"))
            self.assertEqual(time(5, 6, 3, 1), self.time_type("5:6:3:1"))
            self.assertEqual("24:2:1", self.time_type("24:2:1"))


class TestTwoDimensionalNumberArrayType(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.array_type = None

    def test_call(self):
        with mock.patch.object(self, "array_type",
                            TwoDimensionalNumberArrayType("(?P<number>-?\d+)")):
            self.assertEqual([[1.0], [2.0], [3.0], [4.0], [5.0], [6.0]], self.array_type("1, 2, 3, 4, 5, 6"))
        with mock.patch.object(self, "array_type",
                            TwoDimensionalNumberArrayType("(?P<number>-?\d+(\.\d+)?)", item_array_size=3)):
            self.assertEqual([[1.0, -2.0 , 3.0], [-6.0]], self.array_type("(1, -2, 3) >> (-6.0)"))
