from src.containers import LogContainer


class Child1Container(LogContainer):
    pattern = r"child1:\s(?P<name>.*)"
    representative = "child1"


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


class InferTypeTrueContainter(LogContainer):
    pattern = r"father:\s(?P<father>.*)"
    inter_type = True


class InferTypeFalseContainer(LogContainer):
    pattern = r"mother:\s(?P<mother>.*)"
    infer_type = False


class InterTypeConflictsContainer(LogContainer):
    sub_containers = [InferTypeFalseContainer,
                      InferTypeTrueContainter]


class MissingGroupContainer(LogContainer):
    pattern = r".*"