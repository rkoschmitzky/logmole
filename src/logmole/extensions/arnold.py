from ..containers import LogContainer
from ..types import (TypeAssumptions,
                     KeyValueType
                     )


class ArnoldLightsContainer(LogContainer):
    pattern = r"\s?there\sare\s(?P<count>\d+)\slight"
    representative = "lights"


class ArnoldMemoryContainer(LogContainer):
    pattern = r"\|\s+(?P<memory_consumption>[\w\s]+(\d+\.\d{2})$)"


class ArnoldRaysContainer(LogContainer):
    pattern = r"\s(?P<count>\w+\s+\d+)\s\(\s*\d+\.\d+.*(\(\s*\d\.\d+\)\s\(\s*\d+\))$"
    pattern += r"|\|\s+(?P<sample_depths>(diffuse|specular|transmission|volume\sindirect)\s+.*depth\>?\s+\d+)"
    representative = "rays"


class ArnoldShadingContainer(LogContainer):
    pattern = r"\s?(?P<shader_calls>\w+\s+\d+)(\s\(\s*\d+\.\d{2},?\s*\d+\.\d{2}\)\s)\(\s*?\d{1,3}\.\d{2}\%\)$"


class ArnoldSceneContainer(LogContainer):
    sub_containers = [ArnoldShadingContainer,
                      ArnoldRaysContainer,
                      ArnoldMemoryContainer,
                      ArnoldLightsContainer]
    representative = "scene"


class ArnoldPluginsContainer(LogContainer):
    pattern = r".*\|\s*\w*?\s(?P<names>.*)\.(dll|so|dylib):\s(?P<plugins>\w+).*Arnold\s(?P<plugins_arnold_versions>(\d\.?){4})|"
    pattern += r"\|[^\d]*(?P<plugins_count>\d+)\splugin[^\d]*(?P<count>\d+)\slib"


class ArnoldLibrariesContainer(LogContainer):
    pattern = r".*\|\sArnold\s(?P<arnold_version>(\d\.?){4}).*oiio\-(?P<oiio_version>\d+\.\d+\.\d+).*"
    pattern += r"osl\-(?P<osl_version>\d+\.\d+\.\d+)\svdb\-(?P<vdb_version>\d+\.\d+\.\d+)\s"
    pattern += r"clm\-(?P<clm_version>\d+\.\d+\.\d+\.\d+)\srlm\-(?P<rlm_version>\d+\.\d+\.\d+)"
    representative = "libraries"
    sub_containers = [ArnoldPluginsContainer]


class ArnoldRenderTimeContainer(LogContainer):
    pattern = r"\|\s+(?P<rendering>[a-z\s\/\.]+\s+(\d+\:\d{2}\.\d{2})$)"


class ArnoldTimeContainer(LogContainer):
    pattern = r".*log\sstarted.*(?P<start_time>(\d{2}\:?){3})|"
    pattern += r"(?P<total_render_time>(\d+:?){3}).*Arnold\sshutdown"
    representative = "times"
    sub_containers = [ArnoldRenderTimeContainer]


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


class ArnoldImageContainer(LogContainer):
    pattern = r"image\sat\s(?P<width>\d+)\sx\s(?P<height>\d+)|"
    representative = "image"


class ArnoldLogContainer(LogContainer):
    assumptions = TypeAssumptions({
                    ".*\s+\d+\.\d+": KeyValueType(
                                           r"(?P<key>\b(\.?\s?\w+){1,}\b)\s+(?P<value>\d+\.\d+)",
                                           key_type=str,
                                           value_type=float
                                                  ),
                    "\w+\s+(\d+)$": KeyValueType(
                                            r"(?P<key>\w+)\s+(?P<value>\d+)",
                                            key_type=str,
                                            value_type=int
                                                ),
                    ".*\s+\d+\:\d{2}\.\d{2}": KeyValueType(
                                            r"(?P<key>\b(\.?\(?\d?\/?\s?\w+){1,}\b)\s+(?P<value>.*)",
                                            key_type=str,
                                            value_type=str
                                                          ),
                    ".*\s+\d+\s+\/\s+\w+\s+\d+": KeyValueType(
                                                        r"(?P<key>\w+)\s+(?P<value>\d+)",
                                                        value_type=int,
                                                        prefix_pattern=r"(?P<key>^\w+\s)"
                                                                    )


                                   }
                                  )
    sub_containers = [ArnoldHostContainer,
                      ArnoldTimeContainer,
                      ArnoldLibrariesContainer,
                      ArnoldSceneContainer,
                      ArnoldImageContainer]
