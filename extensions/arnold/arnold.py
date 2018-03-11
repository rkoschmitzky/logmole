from src.containers import LogContainer
from src.types import TypeAssumptions, KeyValueType


class ArnoldTypeAssumption(TypeAssumptions):
    def __init__(self):
        super(ArnoldTypeAssumption, self).__init__()
        self[".*\s+\d+\.\d+"] = KeyValueType(r"(?P<key>\b(\.?\s?\w+){1,}\b)\s+(?P<value>\d+\.\d+)",
                                             key_type=str,
                                             value_type=float
                                             )


class ArnoldMemoryContainer(LogContainer):
    pattern = "\|\s+(?P<memory>.*\s+(\d+\.\d{2})$)"


class ArnoldPluginsContainer(LogContainer):
    pattern = "\|\s*\w*?\s(?P<names>.*)\.(dll|so|dylib):\s(?P<plugins>\w+).*Arnold\s(?P<plugin_versions>(\d\.?){4})|"
    pattern += "\|[^\d]*(?P<plugins_number>\d+)\splugin[^\d]*(?P<number>\d+)\slib"
    representative = "libraries"


class ArnoldTimeContainer(LogContainer):
    pattern = ".*log\sstarted.*(?P<start_time>(\d{2}\:?){3})"
    representative = "times"


class ArnoldHostContainer(LogContainer):
    pattern = ".*host\s+application:.*(?P<name>(Maya|Katana|Houdini))\s+(?P<host_version>.*$)"
    representative = "host"


class ArnoldLogContainer(LogContainer):
    pattern = ".*\|\sArnold\s(?P<version>(\d\.?){4})"
    assumptions = ArnoldTypeAssumption()
    sub_containers = [ArnoldHostContainer,
                      ArnoldTimeContainer,
                      ArnoldPluginsContainer,
                      ArnoldMemoryContainer]
