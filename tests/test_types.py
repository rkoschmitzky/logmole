from unittest import TestCase

from src import TypeAssumptions


class TestTypeAssumptions(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._assumptions = TypeAssumptions()

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
        self.assertEqual("NUll", self._assumptions.call_action("NUll"))