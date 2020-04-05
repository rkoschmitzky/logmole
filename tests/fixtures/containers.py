from ...src.logmole import LogContainer
from ...src.logmole import (
    TypeAssumptions,
    KeyValueType
)


class Child1Container(LogContainer):
    pattern = r"child1:\s(?P<name>.*)"
    representative = "child1"
    bla = 5


class Child2Container(LogContainer):
    pattern = r"child2:\s(?P<name>.*)"
    representative = "child2"


class ChildrenContainer(LogContainer):
    sub_containers = [Child1Container,
                      Child2Container]
    representative = "children"


class MotherContainer(LogContainer):
    pattern = r"mother:\s(?P<mother>.*)"
    representative = "parents"


class FatherContainer(LogContainer):
    pattern = r"father:\s(?P<father>.*)"
    representative = "parents"


class ParentsContainer(LogContainer):

    sub_containers = [MotherContainer,
                      FatherContainer,
                      ChildrenContainer]


class InferTypeTrueContainer(LogContainer):
    pattern = r"father:\s(?P<father>.*)"
    inter_type = True


class InferTypeFalseContainer(LogContainer):
    pattern = r"mother:\s(?P<mother>.*)"
    infer_type = False


class InterTypeConflictsContainer(LogContainer):
    sub_containers = [InferTypeFalseContainer,
                      InferTypeTrueContainer]


class MissingGroupContainer(LogContainer):
    pattern = r".*"


class MultiMatchContainer(LogContainer):
    pattern = r".*:\s(?P<family>.*)"


class MultiMatchToDictContainer(LogContainer):
    pattern = r"(?P<family>.*)"
    assumptions = TypeAssumptions({".*": KeyValueType(r"(?P<key>.*):\s(?P<value>.*)")})



