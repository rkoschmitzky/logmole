from ..containers import LogContainer
from ..types import (TypeAssumptions,
                     KeyValueType
                     )


class ArnoldMemoryContainer(LogContainer):
    pattern = r"\|\s+(?P<memory>.*\s+(\d+\.\d{2})$)"
    representative = "scene"


class ArnoldSceneContainer(LogContainer):
    pattern = r"\s(?P<ray_count>\w+\s+\d+)\s\(\s*\d+\.\d+.*(\(\s*\d\.\d+\)\s\(\s*\d+\))$"
    representative = "scene"


class ArnoldPluginsContainer(LogContainer):
    pattern = r".*\|\s*\w*?\s(?P<names>.*)\.(dll|so|dylib):\s(?P<plugins>\w+).*Arnold\s(?P<plugin_versions>(\d\.?){4})|"
    pattern += r"\|[^\d]*(?P<plugins_number>\d+)\splugin[^\d]*(?P<number>\d+)\slib"
    representative = "libraries"


class ArnoldTimeContainer(LogContainer):
    pattern = r".*log\sstarted.*(?P<start>(\d{2}\:?){3})|"
    pattern += r"(?P<total>(\d+:?){3}).*Arnold\sshutdown"
    representative = "times"


class ArnoldAppContainer(LogContainer):
    pattern = r".*host\s+application:.*(?P<name>(Maya|Katana|Houdini))\s+(?P<version>.*$)"
    representative = "app"


class ArnoldMachineContainer(LogContainer):
    pattern = r"running\son\s(?P<name>.*),\s*pid=(?P<pid>\d+)"
    representative = "machine"


class ArnoldHostContainer(LogContainer):
    sub_containers = [ArnoldMachineContainer,
                      ArnoldAppContainer]
    representative = "host"


class ArnoldLogContainer(LogContainer):
    pattern = ".*\|\sArnold\s(?P<version>(\d\.?){4})"
    assumptions = TypeAssumptions({".*\s+\d+\.\d+":
                                       KeyValueType(r"(?P<key>\b(\.?\s?\w+){1,}\b)\s+(?P<value>\d+\.\d+)",
                                                    key_type=str,
                                                    value_type=float
                                                    ),
                                   "\w+\s+(\d+)$":
                                        KeyValueType(r"(?P<key>\w+)\s+(?P<value>\d+)",
                                                     key_type=str,
                                                     value_type=int)
                                   }
                                  )
    sub_containers = [ArnoldHostContainer,
                      ArnoldTimeContainer,
                      ArnoldPluginsContainer,
                      ArnoldSceneContainer,
                      ArnoldMemoryContainer]
