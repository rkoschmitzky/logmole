from src.containers import LogContainer


class ArnoldPluginsContainer(LogContainer):
    pattern = ".*\|\s*\w*?\s(?P<libraries>.*)\.dll"
    representative = "plugins"


class ArnoldTimeContainer(LogContainer):
    pattern = ".*log\sstarted.*(?P<start_time>(\d{2}\:?){3})"
    representative = "times"


class ArnoldHostContainer(LogContainer):
    pattern = ".*host\s+application:.*(?P<name>(Maya|Katana|Houdini))\s+(?P<host_version>.*$)"
    representative = "host"


class ArnoldLogContainer(LogContainer):
    pattern = ".*\|\sArnold\s(?P<version>(\d\.?){4})"
    sub_containers = [ArnoldHostContainer, ArnoldTimeContainer, ArnoldPluginsContainer]
