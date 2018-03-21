# Logmole

## An Extendable and Versatile Logparsing System

Logmole allows you dealing with regex pattern chaining in a simple way to create extensions for different types of
log files.

### Table of Contents

- [Project Goals](#what-can-it-do-for-you)
- [How to use](#how-to-use)
- [Available Extensions](#available-extensions)


### What can it do for you?
- provide a framework to create reusable and modular logparsers based on regular expressions
- simplify the process of chaining multiple regex patterns
- dynamic object and attributes creation based on named capturing groups and representatives
- help with automatic and robust type conversions
- ships with some pre-build extensions

**Contrary to, what have you to do?**
- write extensions and contribute


### How to use

##### LogContainters

The LogContainer class is a component that represents the content of a regex pattern or patterns of its subcontainers.

| Attribute               | Type     | Description
|:------------------------|:---------|:------------
| `pattern    `           | `str`    | The regex pattern a container will use to parse the data. Be aware that you always have to provide a named capturing group. Each match on the named group will end up as its own attribute on the container or the declared container representative.
| `representative`        | `str`    | A name that represents one or multiple containers and defines where to store a containers matched data.
| `sub_containers`        | `str`    | Defines the association of a container with child containers.
| `assumptions`           | sublcass of `BaseAssumptions` | An assumptions object to declare actions on matched data.


### Available Extensions

- [Arnold Renderer](http://solidangle.com/)