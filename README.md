[![Build Status](https://travis-ci.com/rkoschmitzky/logmole.svg?branch=master)](https://travis-ci.com/rkoschmitzky/logmole) [![Coverage Status](https://coveralls.io/repos/github/rkoschmitzky/logmole/badge.svg?branch=master&service=github)](https://coveralls.io/github/rkoschmitzky/logmole?branch=master) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Downloads](https://pepy.tech/badge/logmole)](https://pepy.tech/project/logmole)
# Logmole

## An Extendable and Versatile Logparsing System

Logmole allows you dealing with regex pattern chaining in a simple way to create extensions for different types of
log files.

### Table of Contents

- [Project Goals](#what-can-it-do-for-you)
- [Installation](#installation)
- [How to use](#how-to-use)
  - [LogContainer](#the-logcontainer)
  - [Patterns](#patterns)
  - [Grouping Containers](#grouping-containers)
  - [Assumptions](#assumptions)
    - [Native Type Assumptions](#native-type-assumptions)
    - [Custom Type Assumptions](#custom-type-assumptions)
    - [Custom Types](#custom-types)
- [Included Extensions](#included-extensions)
  - [Arnold Renderer Extension](#arnold-renderer-extension)
    - [Available Fields](#available-arnoldlogcontainer-fields)
- [Planned Extensions](#planned-extensions)
- [Versioning](#versioning)

### What can it do for you?
- provide a framework to create reusable and modular logparsers based on regular expressions
- simplify the process of chaining multiple regex patterns
- dynamic object and fields creation based on named capturing groups and representatives
- help with automatic and robust type conversions
- offer some pre-build extensions

**Contrary to, what do you have to do?**
- write extensions and contribute

-----

### Installation

Logmole can be installed via `pip`.
```bash
pip install logmole
```

### How to use

##### The LogContainer

The LogContainer class is a component that represents the content of a regex pattern or patterns of its sub-containers.

| Attribute               | Type     | Description
|:------------------------|:---------|:------------
| `pattern    `           | `str`    | The regex pattern a container will use to parse the data. Be aware that you always have to provide a named capturing group. Each match on the named group will end up as its own attribute on the container or the declared container representative.
| `representative`        | `str`    | A name that represents one or multiple containers and defines where to store a containers matched data.
| `sub_containers`        | `str`    | Defines the association of a container with child containers.
| `assumptions`           | sublcass of `BaseAssumptions` | An assumptions object to declare actions on matched data.
| `infer_type`            | `bool`   | If True (default) it will use the declared assumptions to convert the type of a match automatically.

| Methods                             | Returns  | Description
|:------------------------------------|:---------|:------------
| `dump(filepath=str, **kwargs)`      | `None`   | Serialize LogContainer representation as a JSON formatted stream to the given filepath. Uses the same signature as json.dump()
| `get_value(str)`                    | `str`    | Get the value of an attribute using a dot separated like `foo.bar.foobar`

----

#### Understand By Example

Lets have a look at some examples to demonstrate the main concepts.


Input Log Content
```bash
19:22:40 | INFO     line 8 in <module> | Movie started
19:22:40 | WARNING  line 10 in <module> | Found 10000 ghosts
19:22:41 | DEBUG    line 12 in <module> | Scene contains 3 Monsters
19:22:43 | DEBUG    line 13 in <module> | Scene contains 1 Girl
19:22:46 | INFO     line 14 in <module> | Movie ends
```

<br>

###### Patterns

Assume our extension only includes a pattern like this that shall provide the start end end time.
```python

from logmole import LogContainer

class MovieLog(LogContainer):
    pattern = "(?P<start_time>.\d+\:\d+:\d+).*started|(?P<end_time>.\d+\:\d+:\d+).*ends"
```
```python
>>> log = MovieLog("C:\\tmp\\some.log")
>>> print log

{
    "end_time": "19:22:46",
    "start_time": "19:22:40"
}
```

The LogContainer gets represented as prettified dictionary. But contrary to that you can use it as object that holds attributes for each capturing group.
```python
>>> print log.start_time
>>> print log.end_time

19:22:40
19:22:46
```

<br>

###### Grouping Containers

Instead of dealing with naming conventions categorize your matches you can define a representative for them.
This doesn't makes sense necessarily if you are working with a small amount of containers, but it will help when creating more complex nestings.
```python
class TimesContainer(LogContainer):
    pattern = "(?P<start>.\d+\:\d+:\d+).*started|(?P<end>.\d+\:\d+:\d+).*ends"
    representative = "times"


class MovieLog(LogContainer):
    sub_containers = [TimesContainer]
```

```python
>>> log = MovieLog("C:\\tmp\\some.log")
>>> print log
>>> print "-"*10
>>> print log.times.start
>>> print log.times.end

{
    "times": {
        "start": "19:22:40",
        "end": "19:22:46"
    }
}
----------
19:22:40
19:22:46
```
As you can see it will create a parent representative and attaches the matches to it.

<br>

Grouping of containers only makes sense if you use the representative, right?
```python
class GhostsContainer(LogContainer):
    pattern = r"(?P<spooky_ghosts>\d+)\s+ghosts?"
    representative = "scene"


class EntitiesContainer(LogContainer):
    pattern = r"contains\s(?P<entities>\d+\s.*)"
    representative = "scene"


class TimesContainer(LogContainer):
    pattern = r"(?P<start>.\d+\:\d+:\d+).*started|(?P<end>.\d+\:\d+:\d+).*ends"
    representative = "times"


class MovieLog(LogContainer):
    sub_containers = [TimesContainer,
                      GhostsContainer,
                      EntitiesContainer]
```

```
>>> log = MovieLog("C:\\tmp\\some.log")
>>> print log

{
    "scene": {
        "entities": [
            "3 Monsters",
            "1 Girl"
        ],
        "spooky_ghosts": 10000
    },
    "times": {
        "start": "19:22:40",
        "end": "19:22:46"
    }
}
```

<br>

But this doesn't mean that a sub container can't have its own sub containers.
Rewriting the extension to look like this would give us the same result.
You are flexible how to stack and layer your containers.
```python
class GhostsContainer(LogContainer):
    pattern = r"(?P<spooky_ghosts>\d+)\s+ghosts?"


class EntitiesContainer(LogContainer):
    pattern = r"contains\s(?P<entities>\d+\s.*)"


class SceneContainer(LogContainer):
    sub_containers = [GhostsContainer,
                      EntitiesContainer]
    representative = "scene"


class TimesContainer(LogContainer):
    pattern = r"(?P<start>.\d+\:\d+:\d+).*started|(?P<end>.\d+\:\d+:\d+).*ends"
    representative = "times"


class MovieLog(LogContainer):
    sub_containers = [TimesContainer,
                      SceneContainer]
```

<br>

###### Assumptions

An Assumptions object defines a set of regex patterns and associates them with actions that gets
called in case there is a match.

Take a look back at the created output again:
```
{
    "scene": {
        "entities": [
            "3 Monsters",
            "1 Girl"
        ],
        "spooky_ghosts": 10000
    },
    "times": {
        "start": "19:22:40",
        "end": "19:22:46"
    }
}
```
Notice that the `scene.spooky_ghosts` entry is not a string anymore. This is because the
`logmole.LogContainer.assumptions` assigns a default `logmole.TypeAssumptions` object
that handles simple conversions automatically.

---

##### Native Type Assumptions

As long as `infer_type ` is set to `True` the LogContainer will always try to convert native
types.

This includes support for:

| Type       | Used Regex
|:-----------|:------------------------------------------------------|
| `int`      | `^(\-?\d+)$`
| `float`    | `(\-?\d+\.\d+)$`
| `None`     | `^((N|n)one)$|^NONE$|^((N|n)ull)$|^NULL$|^((N|n)il)$|^NIL$`


----


You can define whether your container should infer the type or not and disable it by setting
[`infer_type`](#the-logcontainer) to `False`. This only applies to the container itself and doesn't get inherited from
parent containers.
Find out more about [native type assumptions](#native-type-assumptions):

---

##### Custom Type Assumptions

You can also extend existing assumptions or create an individual set of assumptions per container.
Lets demonstrate this on our `TimesContainer` using a custom available [`TimeType`](#timetype) object.
```python
from logmole import (TypeAssumptions,
                     TimeType
                    )
```

```python
class TimesContainer(LogContainer):
    assumptions = TypeAssumptions({".*": TimeType())
    pattern = r"(?P<start>.\d+\:\d+:\d+).*started|(?P<end>.\d+\:\d+:\d+).*ends"
    representative = "times"
```

```python
>>> log = MovieLog("C:\\tmp\\some.log")
>>> print type(log.times.start)
<type 'datetime.time'>
```

A `TypeAssumptions` class has to be initialized with a dictionary defining patterns and their corresponding types.
In our case we can expect that everything that was matched by our `TimesContainer.pattern` before will be
a string of a valid `H:M:S` format. So we don't need a more precise pattern within our TypeAssumptions and can expect
those string would always fulfill the criteria to be convertable by our [`TimeType`](#timetype) object.
The `TypeAssumptions` class always allows us to inherit existing assumptions from parent containers. This is set by default.
You can ignore parent assumptions when initializing the `TypeAssumptions` class using `inherit=False`.
This way you can avoid potential match conflicts when using more sloppy patterns.

But generally spoken your patterns should be as precise as possible when using them on containers that hold a bunch
of sub-containers.

----


#### Custom Types

Native Type conversions might not be sufficient enough for you. There might be cases where you want to convert
your extracted information to a more specific type. There are custom types that can help you doing that or you
can write your own.

##### KeyValueType

**TO BE CONTINUED**


##### TimeType

This object doesn't need any extra information. It will check for a valid input string and return a `datatime.time`
instance.


##### TwoDimensionalNumberArray

An object helpful to convert a string into an even sized two dimensional array with automatic float conversion for each item.
It always expects a `number` named match group within the pattern.

Example:
```python
>>> array_type_1 = TwoDimensionalNumberArray("(?P<number>-?\d+)", item_array_size=1)
>>> array_type_2 = TwoDimensionalNumberArray("(?P<number>-?\d+)", item_array_size=2)
>>> array_type_3 = TwoDimensionalNumberArray("(?P<number>-?\d+)", item_array_size=3)

>>> input = "1, 2, 4 -4, -10, 1"
>>> print array_type_1(input)
>>> print array_type_2(input)
>>> print array_type_3(input)

[[1.0], [2.0], [4.0], [-4.0], [-10.0], [1.0]]
[[1.0, 2.0], [4.0, -4.0], [-10.0, 1.0]]
[[1.0, 2.0, 4.0], [-4.0, -10.0, 1.0]]
```


----

### Included Extensions

#### Arnold Renderer Extension
An extension for the lovely [Arnold Renderer](http://solidangle.com/).

##### Usage
```python
from logmole.extensions import ArnoldLogContainer
arnold_log = ArnoldLogContainer("C:\\tmp\\some_arnold_log.log")
```

----

##### Available ArnoldLogContainer Fields

- `errors`: all errors messages `str` or `list`
- `host`: host information `LogContainer`
  - `app`: name of the host application Arnold is running with `str`
    - `version`: version of the host application Arnold is running with `str`
  - `machine`:
    - `name`: name of the machine Arnold is running on `str`
    - `pid`: process id number `int`
- `image`: image information `LogContainer`
  - `file_path`: path to the generated image `str`
  - `height`: image height `float`
  - `width`: image width `float`
- `libraries`: libraries information `LogContainer`
  - `arnold_version`: Arnold core version `str`
  - `clm_version` clm version `str`
  - `oiio_version` OpenImageIO version `str`
  - `osl_version` OpenShadingLanguage version `str`
  - `plugins` loaded plugins `list`
  - `plugins_ arnold_versions`: arnold version all plugins are using `str` or `list`
  - `plugins_count`: number of loaded plugins `int`
  - `rlm_version`: Reprise License Manager version `str`
  - `vdb_version`: OpenVDB version `str`
- `scene`: scene information `LogContainer`
  - `geometry`: geometry objects information `LogContainer`
    - `count`: number of geometry objects in scene `int`
  - `lights`: scene lights information `LogContainer`
    - `count`: number of lights in scene `int`
    - `samples`: per-light sample & volume sample information `dict`
  - `memory_consumption`: information regarding scene memory usage `dict`
  - `rays`: rays information `LogContainer`
    - `count`: number of rays per type `dict`
    - `sample_depths`: sample and depth information per type `dict`
  - `shader_calls` shader calls per type `dict`
- `times`: time related information `LogContainer`
  - `rendering`: diverse times `dict`
  - `start`: render start time `datetime.time`
- `warnings`: all warning messages `str` or `list`

----

### Planned Extensions
- [Redshift Renderer](https://www.redshift3d.com/)
- [Pixars RenderMan]()
- [VRay]()


### Versioning

`Logmole` follows [semantic versioning](https://semver.org/).
Extensions will not be considered as an public API.
a
