# Logmole

## An Extendable and Versatile Logparsing System

Logmole allows you dealing with regex pattern chaining in a simple way to create extensions for different types of
log files.

### Table of Contents

- [Project Goals](#what-can-it-do-for-you)
- [How to use](#how-to-use)
  - [LogContainer](#the-logcontainer)
  - [Patterns](#patterns)
  - [Grouping Containers](#grouping-containers)
  - [Assumptions](#assumptions)
- [Included Extensions](#included-extensions)
- [Planned Extensions](#planned-extensions)

### What can it do for you?
- provide a framework to create reusable and modular logparsers based on regular expressions
- simplify the process of chaining multiple regex patterns
- dynamic object and attributes creation based on named capturing groups and representatives
- help with automatic and robust type conversions
- ships with some pre-build extensions

**Contrary to, what have you to do?**
- write extensions and contribute

-----

### How to use

##### The LogContainer

The LogContainer class is a component that represents the content of a regex pattern or patterns of its sub-containers.

| Attribute               | Type     | Description
|:------------------------|:---------|:------------
| `pattern    `           | `str`    | The regex pattern a container will use to parse the data. Be aware that you always have to provide a named capturing group. Each match on the named group will end up as its own attribute on the container or the declared container representative.
| `representative`        | `str`    | A name that represents one or multiple containers and defines where to store a containers matched data.
| `sub_containers`        | `str`    | Defines the association of a container with child containers.
| `assumptions`           | sublcass of `BaseAssumptions` | An assumptions object to declare actions on matched data.

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
19:22:46 | INFO     line 14 in <module> | Movie finished
```

<br>

###### Patterns

Assume our extension only includes a pattern like this that shall provide the start end end time.
```python
class MovieLog(LogContainer):
    pattern = "(?P<start_time>.\d+\:\d+:\d+).*started|(?P<end_time>.\d+\:\d+:\d+).*finished"
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
    pattern = "(?P<start>.\d+\:\d+:\d+).*started|(?P<end>.\d+\:\d+:\d+).*finished"
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
    pattern = "(?P<start>.\d+\:\d+:\d+).*started|(?P<end>.\d+\:\d+:\d+).*finished"
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
    pattern = "(?P<start>.\d+\:\d+:\d+).*started|(?P<end>.\d+\:\d+:\d+).*finished"
    representative = "times"


class MovieLog(LogContainer):
    sub_containers = [TimesContainer,
                      SceneContainer]
```

<br>

###### Assumptions
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
`logmole.LogContainer.assumptions` assigns a default `logmole.TypeAssertions` object
that handles simple conversions.

An Assumptions object defines a set of regex patterns and associates them with actions that gets
called in case there is a match.




----

### Included Extensions

- [Arnold Renderer (in progress)](http://solidangle.com/)

----

### Planned Extensions
- [Redshift Renderer]()
- [Pixars RenderMan]()
- [VRay]()