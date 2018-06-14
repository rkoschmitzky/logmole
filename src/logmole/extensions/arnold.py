from ..containers import LogContainer
from ..types import (TypeAssumptions,
                     KeyValueType,
                     TwoDimensionalNumberArray
                     )

AI_LIGHT_TYPES = [
    "point_light",
    "distant_light",
    "quad_light",
    "spot_light",
    "skydome_light",
    "cylinder_light",
    "disk_light",
    "mesh_light",
    "photometric_light"
    ]


class ArnoldErrorsContainer(LogContainer):
    pattern = r"ERROR\s+\|\s+(?P<errors>.*)"


class ArnoldWarningsContainer(LogContainer):
    pattern = r"WARNING\s+\|\s+(?P<warnings>.*)"


class ArnoldMemoryContainer(LogContainer):
    pattern = r"\|\s+(?P<memory_consumption>[\w\s]+(\d+\.\d{2})$)"


class ArnoldRaysContainer(LogContainer):
    pattern = r"\s(?P<count>\w+\s+\d+)\s\(\s*\d+\.\d+.*(\(\s*\d\.\d+\)\s\(\s*\d+\))$"
    pattern += r"|\|\s+(?P<sample_depths>(diffuse|specular|transmission|volume\sindirect)\s+.*depth\>?\s+\d+)"
    pattern += r"|(?P<anti_aliasing_samples>\d+)\sAA\ssamples?"

    assumptions = TypeAssumptions({
            # ray depth and samples coversion
            # "<ray_type>     samples  <nr> / depth  <nr>" to {"<ray_type> samples": <nr>, "<ray_type> depth": <nr>}
            ".*\s+\d+\s+\/\s+\w+\s+\d+": KeyValueType(
                r"(?P<key>\w+)\s+(?P<value>\d+)",
                value_type=int,
                prefix_pattern=r"(?P<key>^\w+\s)"
            )
        }
    )

    representative = "rays"


class ArnoldShadingContainer(LogContainer):
    pattern = r"\s?(?P<shader_calls>\w+\s+\d+)(\s\(\s*\d+\.\d{2},?\s*\d+\.\d{2}\)\s)\(\s*?\d{1,3}\.\d{2}\%\)$"


class ArnoldLightsCountContainer(LogContainer):
    pattern = r"|".join(["\s+\|\s+(?P<{0}s>\d+)\s{0}$".format(_) for _ in AI_LIGHT_TYPES])
    representative = "count"


class ArnoldLightSamplesContainer(LogContainer):
    pattern = r"(?P<samples>\w+\:\s+\w+\_light.*sample.*samples?$)"
    assumptions = TypeAssumptions(
        {
            # light samples and volume samples conversion
            # <light>: <nr> samples <nr> volume samples to {"<light> samples": <nr>, "<light> volume samples": <nr>
            "\w+:(\s\w+){2}\s\d+\s\w+,\s\d+(\s\w+)": KeyValueType(
                r"(?P<value>\d+)\s(?P<key>samples?|volume\ssamples?)",
                value_type=int,
                prefix_pattern=r"(?P<key>\w+):"
            )
        }
    )
    representative = "lights"


class ArnoldLightsContainer(LogContainer):
    sub_containers = [ArnoldLightsCountContainer,
                      ArnoldLightSamplesContainer]
    representative = "lights"


class ArnoldGeometryContainer(LogContainer):
    pattern = r"\|\s+(?P<count>\d+\s(polymesh|curves)$)"
    representative = "geometry"


class ArnoldSceneContainer(LogContainer):
    pattern = r"\|\s+scene\sbounds:\s(?P<bounds>\(.*\)$)"
    assumptions = TypeAssumptions({
        # scene bounds conversion "(x x x) -> (x x x)" to  [[x, x, x], [x, x, x]]
        "\(.*\)\s-\>\s\(.*\)": TwoDimensionalNumberArray(
            r"(?P<number>-?\d+(\.\d+)?)",
            item_array_size=3
            )
        }
    )
    sub_containers = [ArnoldShadingContainer,
                      ArnoldRaysContainer,
                      ArnoldMemoryContainer,
                      ArnoldLightsContainer,
                      ArnoldGeometryContainer]
    representative = "scene"


class ArnoldPluginsContainer(LogContainer):
    pattern = r".*\|\s*\w*?\s(?P<names>.*)\.(dll|so|dylib):\s(?P<plugins>\w+).*Arnold\s(?P<plugins_arnold_versions>(\d\.?){4})"
    pattern += r"|\|[^\d]*(?P<plugins_count>\d+)\splugin[^\d]*(?P<count>\d+)\slib"


class ArnoldLibrariesContainer(LogContainer):
    pattern = r".*\|\sArnold\s(?P<arnold_version>(\d\.?){4}).*oiio\-(?P<oiio_version>\d+\.\d+\.\d+).*"
    pattern += r"osl\-(?P<osl_version>\d+\.\d+\.\d+)\svdb\-(?P<vdb_version>\d+\.\d+\.\d+)\s"
    pattern += r"clm\-(?P<clm_version>\d+\.\d+\.\d+\.\d+)\srlm\-(?P<rlm_version>\d+\.\d+\.\d+)"
    representative = "libraries"
    sub_containers = [ArnoldPluginsContainer]


class ArnoldRenderTimeContainer(LogContainer):
    pattern = r"\|\s+(?P<rendering>[a-z\s\/\.]+\s+(\d+\:\d{2}\.\d{2})$)"


class ArnoldTimeContainer(LogContainer):
    pattern = r".*log\sstarted.*(?P<start_time>(\d{2}\:?){3})"
    pattern += r"|(?P<total_render_time>(\d+:?){3}).*Arnold\sshutdown"
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
    pattern = r"image\sat\s(?P<width>\d+)\sx\s(?P<height>\d+)"
    pattern += r"|writing\sfile\s[\`\'\"](?P<file_path>.*)[\`\'\"]"
    representative = "image"


class ArnoldLogContainer(LogContainer):
    assumptions = TypeAssumptions({
                    # less specific assumptions with higher occurance
                    "[a-zA-Z\s]*\s+\d+\.\d+": KeyValueType(
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
                    # digit any_character conversion into {any_character: int}
                    "^\d+\s[a-z_]+$": KeyValueType(
                        r"(?P<value>\d+)\s(?P<key>.*?)",
                        value_type=int,
                        prefix_pattern=r"(?P<key>[a-z_]*$)"
                        ),

        }
    )
    sub_containers = [ArnoldHostContainer,
                      ArnoldTimeContainer,
                      ArnoldLibrariesContainer,
                      ArnoldSceneContainer,
                      ArnoldImageContainer,
                      ArnoldErrorsContainer,
                      ArnoldWarningsContainer
                      ]
